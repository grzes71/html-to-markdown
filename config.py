"""Configuration module for the html-to-markdown application."""

from __future__ import annotations

from pathlib import Path

# --- Crawling limits ---
MAX_DEPTH: int = 5
MAX_PAGES: int = 500

# --- HTTP settings ---
REQUEST_TIMEOUT: int = 30  # seconds
REQUEST_RETRIES: int = 3
REQUEST_DELAY: float = 0.5  # seconds between requests (politeness)
USER_AGENT: str = (
    "Mozilla/5.0 (compatible; html-to-markdown-bot/1.0; "
    "+https://github.com/example/html-to-markdown)"
)

# --- Output ---
OUTPUT_DIR: Path = Path("output")
DEFAULT_OUTPUT_FILENAME: str = "website.md"
OUTPUT_ENCODING: str = "utf-8"

# --- Content extraction ---
# HTML tags / selectors to exclude from content
EXCLUDE_TAGS: list[str] = [
    "nav", "header", "footer", "aside", "script", "style",
    "noscript", "iframe", "form", "button", "input", "select",
    "textarea", "template", "dialog", "menu",
]
EXCLUDE_CLASSES: list[str] = [
    "nav", "navbar", "navigation", "menu", "sidebar", "footer",
    "header", "cookie", "banner", "advertisement", "ad-", "ads-",
    "social", "share", "comment", "related", "recommended",
    "breadcrumb", "pagination", "skip-link", "screen-reader",
]
EXCLUDE_IDS: list[str] = [
    "nav", "navbar", "navigation", "menu", "sidebar", "footer",
    "header", "cookie", "banner", "advertisement", "comments",
]

# Preferred content selectors (in priority order)
PREFERRED_SELECTORS: list[str] = [
    "article",
    "main",
    '[role="main"]',
    ".post-content",
    ".article-content",
    ".entry-content",
    ".documentation",
    ".markdown-body",
    "#content",
    ".content",
]

# --- Logging ---
LOG_FORMAT: str = "  %(levelname)-8s %(message)s"
LOG_DATE_FORMAT: str = "%H:%M:%S"

# Third-party loggers to silence even in verbose mode
SILENCED_LOGGERS: list[str] = [
    "httpx",
    "httpcore",
    "urllib3",
    "chardet",
    "charset_normalizer",
    "readability",
]
