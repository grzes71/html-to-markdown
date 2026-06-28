"""Content extraction — isolates the main content from cleaned HTML."""

from __future__ import annotations

import logging
import re
import uuid

import trafilatura
from bs4 import BeautifulSoup, NavigableString, Tag
from readability import Document

from config import PREFERRED_SELECTORS
from extractor.html_cleaner import clean_html

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# <pre> block preservation helpers
# ---------------------------------------------------------------------------

_PRE_PLACEHOLDER_RE = re.compile(r"%%PRE_PLACEHOLDER_([a-f0-9]+)%%")


def _shelter_pre_blocks(html: str) -> tuple[str, dict[str, str]]:
    """Replace every ``<pre>…</pre>`` block with a unique placeholder.

    This prevents content extractors (trafilatura, readability) from
    stripping or reformatting verbatim code/preformatted sections.

    Returns:
        (modified_html, {placeholder: original_pre_html})
    """
    soup = BeautifulSoup(html, "lxml")
    shelter: dict[str, str] = {}

    for pre in soup.find_all("pre"):
        if not isinstance(pre, Tag):
            continue
        tag_id = uuid.uuid4().hex[:10]
        placeholder = f"%%PRE_PLACEHOLDER_{tag_id}%%"
        shelter[placeholder] = str(pre)
        pre.replace_with(soup.new_string(placeholder))

    return str(soup), shelter


def _restore_pre_blocks(html: str, shelter: dict[str, str]) -> str:
    """Replace placeholders with the original ``<pre>`` HTML."""
    for placeholder, pre_html in shelter.items():
        html = html.replace(placeholder, pre_html)
    return html

# ---------------------------------------------------------------------------


def extract_content(html: str, url: str = "") -> str:
    """Extract the main content from an HTML page and return cleaned HTML.

    ``<pre>`` blocks are preserved verbatim throughout extraction so
    that code listings and preformatted text survive unchanged.

    Uses a multi-strategy approach:
    1. Try trafilatura for content extraction.
    2. Fall back to readability-lxml.
    3. Fall back to BeautifulSoup with preferred selectors.
    4. Last resort: use cleaned body content.

    Args:
        html: The raw HTML string.
        url: The source URL (for reference).

    Returns:
        Cleaned HTML string containing only main content.
    """
    # Shelter <pre> blocks so trafilatura doesn't strip them
    html, pre_shelter = _shelter_pre_blocks(html)

    # Strategy 1: trafilatura
    try:
        extracted = trafilatura.extract(
            html,
            include_formatting=True,
            include_links=True,
            include_images=False,
            include_tables=True,
            output_format="html",
            url=url,
        )
        if extracted and len(extracted.strip()) > 100:
            extracted = _restore_pre_blocks(extracted, pre_shelter)
            logger.debug("Content extracted via trafilatura (%d chars)", len(extracted))
            return _normalize_whitespace(extracted)
    except Exception as exc:
        logger.debug("trafilatura extraction failed: %s", exc)

    # Restore <pre> blocks for fallback strategies
    html = _restore_pre_blocks(html, pre_shelter)

    # Strategy 2: readability-lxml
    try:
        doc = Document(html)
        summary_html = doc.summary()
        if summary_html and len(summary_html.strip()) > 100:
            logger.debug("Content extracted via readability-lxml (%d chars)", len(summary_html))
            soup = BeautifulSoup(summary_html, "lxml")
            clean_html(soup)
            return _normalize_whitespace(str(soup))
    except Exception as exc:
        logger.debug("readability-lxml extraction failed: %s", exc)

    # Strategy 3: BeautifulSoup with preferred selectors
    soup = BeautifulSoup(html, "lxml")
    clean_html(soup)

    for selector in PREFERRED_SELECTORS:
        element = soup.select_one(selector)
        if element and isinstance(element, Tag):
            text = element.get_text(strip=True)
            if len(text) > 100:
                logger.debug("Content extracted via selector: %s (%d chars)", selector, len(text))
                return _normalize_whitespace(str(element))

    # Strategy 4: body content
    body = soup.find("body")
    if body and isinstance(body, Tag):
        logger.debug("Falling back to body content")
        return _normalize_whitespace(str(body))

    logger.warning("No content extracted from %s", url)
    return ""


def extract_page_title(html: str) -> str:
    """Extract the page title from HTML.

    Args:
        html: Raw HTML string.

    Returns:
        The page title, or empty string if not found.
    """
    soup = BeautifulSoup(html, "lxml")

    # Try og:title first
    og_title = soup.find("meta", property="og:title")
    if og_title and isinstance(og_title, Tag):
        content = og_title.get("content", "")
        if isinstance(content, str) and content.strip():
            return content.strip()

    # Fall back to <title>
    title_tag = soup.find("title")
    if title_tag and isinstance(title_tag, Tag):
        text = title_tag.get_text(strip=True)
        return text

    # Try first h1
    h1 = soup.find("h1")
    if h1 and isinstance(h1, Tag):
        return h1.get_text(strip=True)

    return ""


def _normalize_whitespace(html: str) -> str:
    """Normalize excessive whitespace in HTML.

    Args:
        html: HTML string with potential excessive whitespace.

    Returns:
        HTML string with normalized whitespace.
    """
    # Collapse multiple blank lines
    html = re.sub(r"\n\s*\n\s*\n+", "\n\n", html)
    # Remove leading/trailing whitespace per line
    html = "\n".join(line.strip() for line in html.splitlines())
    return html.strip()
