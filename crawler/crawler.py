"""Core web crawler that downloads pages and discovers links."""

from __future__ import annotations

import logging
import re
import time
from collections import deque

import httpx
from bs4 import BeautifulSoup

import config
from crawler.link_extractor import extract_links
from crawler.url_filter import normalize_url

logger = logging.getLogger(__name__)

type PageContent = tuple[str, str]  # (url, html_content)

# Regex to extract charset from Content-Type header or HTML meta tag
_CHARSET_RE = re.compile(rb'charset[="\s]+([a-zA-Z0-9_-]+)', re.IGNORECASE)


def _detect_encoding(content: bytes, content_type_header: str) -> str:
    """Detect the correct encoding for HTML content.

    Checks in order:
    1. charset from Content-Type HTTP header
    2. charset from HTML <meta> tags (first 2048 bytes)
    3. chardet / charset_normalizer auto-detection
    4. fallback to UTF-8

    Args:
        content: Raw response body bytes.
        content_type_header: Value of the Content-Type HTTP header.

    Returns:
        Encoding name suitable for bytes.decode().
    """
    # 1. Try Content-Type header charset
    header_match = _CHARSET_RE.search(content_type_header.encode("ascii", errors="ignore"))
    if header_match:
        encoding = header_match.group(1).decode("ascii")
        logger.debug("Encoding from HTTP header: %s", encoding)
        return encoding

    # 2. Try HTML meta charset (search first 2048 bytes of content)
    head_chunk = content[:2048]
    meta_match = _CHARSET_RE.search(head_chunk)
    if meta_match:
        encoding = meta_match.group(1).decode("ascii")
        logger.debug("Encoding from HTML meta tag: %s", encoding)
        return encoding

    # 3. Try charset_normalizer / chardet
    try:
        import charset_normalizer

        result = charset_normalizer.from_bytes(content)
        if result:
            best = result.best()
            if best:
                encoding = best.encoding
                logger.debug("Encoding detected by charset_normalizer: %s", encoding)
                return encoding
    except ImportError:
        pass

    try:
        import chardet

        result = chardet.detect(content)
        encoding = result.get("encoding")
        if encoding:
            logger.debug("Encoding detected by chardet: %s", encoding)
            return encoding
    except ImportError:
        pass

    # 4. Fallback to UTF-8
    logger.debug("Could not detect encoding, falling back to UTF-8")
    return "utf-8"


def fetch_page(
    client: httpx.Client,
    url: str,
) -> str | None:
    """Download a single page with retry logic.

    Args:
        client: An httpx Client instance.
        url: The URL to fetch.

    Returns:
        The HTML content as a string, or None on failure.
    """
    headers = {"User-Agent": config.USER_AGENT}

    for attempt in range(1, config.REQUEST_RETRIES + 1):
        try:
            response = client.get(
                url,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
                follow_redirects=True,
            )

            # Don't retry 404s — they won't appear on retry
            if response.status_code == 404:
                logger.warning("  [404] %s", url)
                return None

            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                logger.debug("Skipping non-HTML content at %s (%s)", url, content_type)
                return None

            # Detect the correct encoding and decode the content
            encoding = _detect_encoding(response.content, content_type)
            try:
                return response.content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                # If the detected encoding fails, fall back to httpx's auto-detection
                logger.warning(
                    "Decoding with '%s' failed for %s, falling back to auto-detect",
                    encoding,
                    url,
                )
                return response.text

        except httpx.HTTPStatusError as exc:
            if not _is_retryable_status(exc.response.status_code):
                logger.warning("  [%d] %s", exc.response.status_code, url)
                return None
            logger.warning(
                "HTTP %d for %s (attempt %d/%d)",
                exc.response.status_code,
                url,
                attempt,
                config.REQUEST_RETRIES,
            )
            if attempt < config.REQUEST_RETRIES:
                time.sleep(1 * attempt)
        except httpx.RequestError as exc:
            logger.warning(
                "Request error for %s: %s (attempt %d/%d)",
                url,
                exc,
                attempt,
                config.REQUEST_RETRIES,
            )
            if attempt < config.REQUEST_RETRIES:
                time.sleep(1 * attempt)

    logger.error("Failed to fetch %s after %d attempts", url, config.REQUEST_RETRIES)
    return None


def crawl(
    start_url: str,
    client: httpx.Client | None = None,
) -> list[PageContent]:
    """Crawl a website starting from a URL using BFS.

    Args:
        start_url: The starting URL.
        client: Optional httpx Client. Created if not provided.

    Returns:
        A list of (url, html_content) tuples in crawl order.
    """
    start_url = normalize_url(start_url)
    base_domain = httpx.URL(start_url).host or ""

    own_client = client is None
    if own_client:
        client = httpx.Client()

    try:
        visited: set[str] = set()
        results: list[PageContent] = []
        queue: deque[tuple[str, int]] = deque()
        queue.append((start_url, 0))

        logger.info("Starting crawl from: %s", start_url)
        logger.info("  Domain: %s", base_domain)

        while queue and len(visited) < config.MAX_PAGES:
            url, depth = queue.popleft()

            if url in visited:
                continue
            visited.add(url)

            logger.info("[%d/%d] depth=%d %s", len(visited), config.MAX_PAGES, depth, url)

            html = fetch_page(client, url)
            if html is None:
                continue

            results.append((url, html))

            if depth >= config.MAX_DEPTH:
                logger.debug("Max depth reached at %s", url)
                continue

            # Parse and discover links
            try:
                soup = BeautifulSoup(html, "lxml")
            except Exception:
                logger.warning("Could not parse HTML from %s", url)
                continue

            links = extract_links(soup, url, base_domain)
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))

            # Politeness delay
            if config.REQUEST_DELAY > 0:
                time.sleep(config.REQUEST_DELAY)

        logger.info(
            "Crawl complete: %d pages visited, %d results",
            len(visited),
            len(results),
        )
        return results

    finally:
        if own_client:
            client.close()
