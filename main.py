#!/usr/bin/env python3
"""html-to-markdown — Crawl a website and convert its content to a single Markdown file.

Usage:
    python main.py https://example.com/docs
    python main.py https://example.com/docs -o output/my_docs.md
    python main.py https://example.com/docs --max-depth 3 --max-pages 50
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer

from config import (
    DEFAULT_OUTPUT_FILENAME,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    MAX_DEPTH,
    MAX_PAGES,
    OUTPUT_DIR,
    OUTPUT_ENCODING,
)
from converter.markdown_converter import convert_to_markdown
from crawler.crawler import crawl
from extractor.content_extractor import extract_content, extract_page_title
from merger.document_merger import merge_documents

app = typer.Typer(
    name="html-to-markdown",
    help="Crawl a website and convert its content to a single Markdown file.",
)


def setup_logging(verbose: bool = False) -> None:
    """Configure structured logging.

    Args:
        verbose: If True, set log level to DEBUG.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        stream=sys.stderr,
    )

    # Silence noisy third-party loggers
    from config import SILENCED_LOGGERS

    for logger_name in SILENCED_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


@app.command()
def main(
    url: str = typer.Argument(..., help="The starting URL to crawl."),
    output: Path = typer.Option(
        OUTPUT_DIR / DEFAULT_OUTPUT_FILENAME,
        "--output",
        "-o",
        help="Output Markdown file path.",
    ),
    max_depth: int = typer.Option(
        MAX_DEPTH,
        "--max-depth",
        "-d",
        help="Maximum crawl depth.",
    ),
    max_pages: int = typer.Option(
        MAX_PAGES,
        "--max-pages",
        "-p",
        help="Maximum number of pages to crawl.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose/debug logging.",
    ),
) -> None:
    """Crawl a website and generate a consolidated Markdown document."""
    setup_logging(verbose)
    logger = logging.getLogger("main")

    # Override config with CLI options
    import config

    config.MAX_DEPTH = max_depth
    config.MAX_PAGES = max_pages

    logger.info("=== html-to-markdown ===")
    logger.info("  Start URL:  %s", url)
    logger.info("  Max depth:  %d", max_depth)
    logger.info("  Max pages:  %d", max_pages)
    logger.info("  Output:     %s", output)

    # Step 1: Crawl
    logger.info("--- Crawling ---")
    try:
        pages_html = crawl(url)
    except Exception as exc:
        logger.error("Crawling failed: %s", exc)
        raise typer.Exit(code=1)

    if not pages_html:
        logger.error("No pages were fetched. Exiting.")
        raise typer.Exit(code=1)

    # Step 2: Extract content from each page
    logger.info("--- Extracting content ---")
    pages_markdown: list[tuple[str, str, str]] = []
    for page_url, html in pages_html:
        try:
            title = extract_page_title(html)
            logger.info("  Extracting: %s", title or page_url)
            content_html = extract_content(html, page_url)
            if not content_html:
                logger.warning("  No content extracted from: %s", page_url)
                continue
            markdown = convert_to_markdown(content_html)
            if markdown.strip():
                pages_markdown.append((page_url, title, markdown))
            else:
                logger.warning("  Empty markdown for: %s", page_url)
        except Exception as exc:
            logger.error("  Failed to process %s: %s", page_url, exc)
            continue

    if not pages_markdown:
        logger.error("No content was extracted from any page. Exiting.")
        raise typer.Exit(code=1)

    logger.info("  Extracted content from %d pages", len(pages_markdown))

    # Step 3: Merge documents
    logger.info("--- Merging ---")
    try:
        merged = merge_documents(pages_markdown, url)
    except Exception as exc:
        logger.error("Merging failed: %s", exc)
        raise typer.Exit(code=1)

    # Step 4: Write output
    logger.info("--- Writing output ---")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.write_text(merged, encoding=OUTPUT_ENCODING)
        logger.info("  Output written to: %s", output)
        logger.info("  Size: %d characters", len(merged))
        logger.info("  Pages: %d", len(pages_markdown))
    except OSError as exc:
        logger.error("Failed to write output file: %s", exc)
        raise typer.Exit(code=1)

    logger.info("=== Done ===")


if __name__ == "__main__":
    app()
