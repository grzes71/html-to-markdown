"""Link extraction from HTML pages."""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from crawler.url_filter import (
    is_internal_link,
    resolve_url,
    should_skip_url,
)

logger = logging.getLogger(__name__)


def extract_links(
    soup: BeautifulSoup,
    base_url: str,
    base_domain: str,
) -> list[str]:
    """Extract all internal content links from a parsed HTML page.

    Only returns links that are:
    - Internal (same domain)
    - Not pointing to non-content assets (images, JS, CSS, etc.)
    - Unique (no duplicates)

    Args:
        soup: Parsed BeautifulSoup object.
        base_url: The URL of the current page.
        base_domain: The domain to restrict links to.

    Returns:
        A list of unique, normalized, internal URLs.
    """
    links: set[str] = set()

    for tag in soup.find_all("a", href=True):
        if not isinstance(tag, Tag):
            continue

        href = tag.get("href")
        if not isinstance(href, str):
            continue

        resolved = resolve_url(href.strip(), base_url)
        if not resolved:
            continue

        if not is_internal_link(resolved, base_domain):
            continue

        if should_skip_url(resolved):
            continue

        links.add(resolved)

    logger.debug("Extracted %d unique internal links from %s", len(links), base_url)
    return sorted(links)
