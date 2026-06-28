"""URL filtering and validation utilities."""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse, urlunparse

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """Normalize a URL by removing fragments and trailing slashes.

    Args:
        url: The URL to normalize.

    Returns:
        A normalized URL string without fragments and with consistent trailing slash.
    """
    parsed = urlparse(url)
    # Remove fragment
    cleaned = parsed._replace(fragment="")
    # Remove default ports
    netloc = parsed.netloc
    if (parsed.scheme == "http" and netloc.endswith(":80")) or (
        parsed.scheme == "https" and netloc.endswith(":443")
    ):
        netloc = netloc.rsplit(":", 1)[0]
    cleaned = cleaned._replace(netloc=netloc)
    # Normalize path: remove trailing slash except for root
    path = cleaned.path.rstrip("/") or "/"
    cleaned = cleaned._replace(path=path)
    return urlunparse(cleaned)


def is_same_domain(url: str, base_domain: str) -> bool:
    """Check if a URL belongs to the same domain as the base.

    Args:
        url: The URL to check.
        base_domain: The base domain to compare against.

    Returns:
        True if the URL is on the same domain, False otherwise.
    """
    parsed = urlparse(url)
    return parsed.netloc == base_domain or not parsed.netloc


def is_internal_link(url: str, base_domain: str) -> bool:
    """Determine if a link is internal (same domain, not external).

    Args:
        url: The link URL.
        base_domain: The base domain.

    Returns:
        True if the link is internal, False otherwise.
    """
    if not url:
        return False
    parsed = urlparse(url)
    # Skip non-http schemes
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return False
    # Relative URLs are internal
    if not parsed.netloc:
        return True
    return parsed.netloc == base_domain


def should_skip_url(url: str) -> bool:
    """Check if a URL should be skipped (non-content pages).

    Args:
        url: The URL to check.

    Returns:
        True if the URL should be skipped.
    """
    skip_patterns = [
        # File types to skip
        ".pdf", ".zip", ".tar", ".gz", ".jpg", ".jpeg", ".png",
        ".gif", ".svg", ".ico", ".css", ".js", ".xml", ".json",
        ".woff", ".woff2", ".ttf", ".eot",
        # Common non-content paths
        "/cdn-cgi/", "/wp-admin/", "/wp-json/", "/feed/",
        "/tag/", "/category/", "/author/", "/search", "/print/",
        "mailto:", "javascript:", "tel:", "ftp:",
    ]
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in skip_patterns)


def resolve_url(href: str, base_url: str) -> str | None:
    """Resolve a possibly-relative href against a base URL.

    Handles the common case where the base URL lacks a trailing slash
    (e.g. ``/mapping`` vs ``/mapping/``), which would cause ``urljoin``
    to replace the last path segment rather than appending to it.

    Args:
        href: The href attribute value.
        base_url: The base URL of the page.

    Returns:
        The resolved absolute URL, or None if invalid.
    """
    if not href:
        return None

    # Strip fragment/anchor from href (they're page-internal)
    if "#" in href:
        href = href.split("#", 1)[0]
        if not href:
            return None

    try:
        # Ensure the base URL is treated as a directory for relative
        # link resolution.  Without a trailing slash, urljoin replaces
        # the last path segment (e.g. /mapping) instead of appending.
        parsed_base = urlparse(base_url)
        path = parsed_base.path or "/"
        if not path.endswith("/"):
            last_segment = path.rsplit("/", 1)[-1]
            # If the last segment does not look like a file, add a slash
            if "." not in last_segment:
                base_url = urlunparse(parsed_base._replace(path=path + "/"))

        resolved = urljoin(base_url, href)
        return normalize_url(resolved)
    except ValueError:
        logger.debug("Could not resolve URL: %r from %r", href, base_url)
        return None
