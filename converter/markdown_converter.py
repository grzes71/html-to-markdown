"""HTML-to-Markdown conversion using markdownify."""

from __future__ import annotations

import logging
import uuid
from typing import NamedTuple

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md_convert

logger = logging.getLogger(__name__)


class _PreBlock(NamedTuple):
    """Holds the verbatim text of a <pre> element before conversion."""

    placeholder: str
    text: str


def _extract_pre_blocks(html: str) -> tuple[str, list[_PreBlock]]:
    """Find all <pre> elements, replace them with placeholders,
    and return the modified HTML plus the extracted blocks.

    The text inside <pre> is taken verbatim (``.get_text()``), which
    strips any nested HTML tags so they appear as literal source code
    in the final Markdown fenced code block.
    """
    soup = BeautifulSoup(html, "lxml")
    blocks: list[_PreBlock] = []

    for pre in soup.find_all("pre"):
        if not isinstance(pre, Tag):
            continue

        text = pre.get_text()  # strips inner HTML, preserves whitespace
        tag_id = uuid.uuid4().hex[:12]
        placeholder = f"%%PREBLOCK_{tag_id}%%"

        pre.replace_with(soup.new_string(placeholder))
        blocks.append(_PreBlock(placeholder=placeholder, text=text))

    return str(soup), blocks


def _restore_pre_blocks(markdown: str, blocks: list[_PreBlock]) -> str:
    """Replace placeholder strings with fenced code blocks."""
    for block in blocks:
        # Surround with blank lines so the code block is properly separated
        fenced = f"\n\n```\n{block.text}\n```\n\n"
        markdown = markdown.replace(block.placeholder, fenced)
    return markdown


def convert_to_markdown(html: str, heading_style: str = "ATX") -> str:
    """Convert cleaned HTML content to Markdown.

    ``<pre>`` elements are treated as verbatim code blocks: their
    inner HTML tags are stripped and the raw text is wrapped in
    fenced code fences (`` ``` ``).

    Args:
        html: Cleaned HTML string.
        heading_style: Heading style — "ATX" (#) or "SETEXT" (underlines).

    Returns:
        Markdown string.
    """
    if not html.strip():
        return ""

    # ---- extract <pre> blocks before conversion ---------------------------
    html, pre_blocks = _extract_pre_blocks(html)

    try:
        markdown = md_convert(
            html,
            heading_style=heading_style,
            bullets="-",
            strip=["script", "style", "img"],
            escape_underscores=False,
            escape_asterisks=False,
        )
    except Exception as exc:
        logger.warning("markdownify conversion failed: %s, falling back to strip", exc)
        markdown = BeautifulSoup(html, "lxml").get_text()
        logger.debug("Fell back to plain text extraction")

    # ---- restore <pre> blocks as fenced code blocks -----------------------
    markdown = _restore_pre_blocks(markdown, pre_blocks)

    return _clean_markdown(markdown)


def _clean_markdown(markdown: str) -> str:
    """Post-process Markdown to clean up common artifacts.

    Args:
        markdown: Raw Markdown string.

    Returns:
        Cleaned Markdown string.
    """
    lines = markdown.splitlines()
    cleaned: list[str] = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()

        # Collapse multiple consecutive blank lines
        if not stripped:
            if not prev_blank:
                cleaned.append("")
                prev_blank = True
            continue
        prev_blank = False

        # Remove excessive inline whitespace
        stripped = " ".join(stripped.split())
        cleaned.append(stripped)

    # Strip leading/trailing blank lines
    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()

    return "\n".join(cleaned)
