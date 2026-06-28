"""Document merger — combines Markdown from multiple pages into one document."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def merge_documents(
    pages: list[tuple[str, str, str]],
    start_url: str = "",
) -> str:
    """Merge multiple pages of Markdown content into a single document.

    Each page is separated by a horizontal rule and prefixed with its title.

    Args:
        pages: List of (url, title, markdown_content) tuples.
        start_url: The original start URL (for the document header).

    Returns:
        A consolidated Markdown string.
    """
    if not pages:
        return "# No content\n\nNo pages were successfully processed."

    sections: list[str] = []

    for i, (url, title, content) in enumerate(pages):
        if not content.strip():
            continue

        section_parts: list[str] = []

        if i == 0:
            # First page gets the H1 heading
            heading = title or _extract_heading_from_markdown(content) or "Documentation"
            section_parts.append(f"# {heading}")
        else:
            # Subsequent pages get H2 with their title
            heading = title or _extract_heading_from_markdown(content) or f"Page {i + 1}"
            section_parts.append(f"## {heading}")

        section_parts.append("")

        # Adjust heading levels: shift all headings down by 1 for subsequent pages
        if i == 0:
            # For the first page, demote H1→H2, H2→H3, etc.
            adjusted = _shift_headings(content, shift=1)
        else:
            adjusted = content

        section_parts.append(adjusted)
        sections.append("\n".join(section_parts))

    # Join sections with horizontal rules
    document = "\n\n---\n\n".join(sections)

    # Add source URL note at the bottom
    if start_url:
        document += f"\n\n---\n\n*Generated from: <{start_url}>*"

    return document


def _extract_heading_from_markdown(content: str) -> str:
    """Extract the first heading from Markdown content.

    Args:
        content: Markdown string.

    Returns:
        The heading text without the # prefix, or empty string.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            # Remove leading # marks and whitespace
            return re.sub(r"^#+\s*", "", stripped)
    return ""


def _shift_headings(content: str, shift: int = 1) -> str:
    """Shift all heading levels in Markdown content.

    Args:
        content: Markdown string.
        shift: Number of levels to shift (positive = demote).

    Returns:
        Markdown with shifted heading levels.
    """
    if shift <= 0:
        return content

    def _replace(match: re.Match[str]) -> str:
        level = len(match.group(1))
        return "#" * min(level + shift, 6) + match.group(2)

    return re.sub(r"^(#{1,6})(\s.*)$", _replace, content, flags=re.MULTILINE)
