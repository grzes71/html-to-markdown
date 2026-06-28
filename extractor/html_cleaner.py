"""HTML cleaning — removes non-content elements before extraction."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from config import EXCLUDE_CLASSES, EXCLUDE_IDS, EXCLUDE_TAGS


def clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove non-content elements from parsed HTML.

    Removes scripts, styles, nav, header, footer, ads, cookie banners, etc.

    Args:
        soup: A BeautifulSoup object to clean in-place.

    Returns:
        The same BeautifulSoup object (mutated in-place).
    """
    # Remove tags by tag name
    for tag_name in EXCLUDE_TAGS:
        for element in soup.find_all(tag_name):
            element.decompose()

    # Remove elements by class pattern matching
    for element in soup.find_all(class_=True):
        if not isinstance(element, Tag):
            continue
        classes = element.get("class")
        if isinstance(classes, list):
            class_str = " ".join(classes).lower()
            if any(exc in class_str for exc in EXCLUDE_CLASSES):
                element.decompose()

    # Remove elements by id pattern matching
    for element in soup.find_all(id=True):
        if not isinstance(element, Tag):
            continue
        elem_id = str(element.get("id", "")).lower()
        if any(exc in elem_id for exc in EXCLUDE_IDS):
            element.decompose()

    # Remove hidden elements
    for element in soup.find_all(style=True):
        if not isinstance(element, Tag):
            continue
        style = str(element.get("style", "")).lower()
        if "display: none" in style or "visibility: hidden" in style:
            element.decompose()

    for element in soup.find_all(attrs={"hidden": True}):
        element.decompose()

    # Remove empty elements that are just containers
    _remove_empty_containers(soup)

    return soup


def _remove_empty_containers(soup: BeautifulSoup) -> None:
    """Remove div/span elements that have no text content.

    Args:
        soup: The BeautifulSoup object to clean.
    """
    for tag_name in ("div", "span", "section"):
        for element in soup.find_all(tag_name):
            if not isinstance(element, Tag):
                continue
            text = element.get_text(strip=True)
            if not text:
                element.decompose()
