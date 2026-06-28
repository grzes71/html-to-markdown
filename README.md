# html-to-markdown

A Python command-line tool that crawls a website starting from a given URL, extracts meaningful content from its pages, converts it to Markdown, and merges everything into a single consolidated `.md` document.

Non-content elements — navigation menus, advertisements, cookie banners, footers, sidebars, and tracking scripts — are automatically stripped during extraction.

## Features

- **Recursive crawling** — follows internal links within the same domain, configurable depth and page limits
- **Multi-strategy content extraction** — uses [trafilatura](https://github.com/adbar/trafilatura), [readability-lxml](https://github.com/buriy/python-readability), and BeautifulSoup with preferred selectors, falling back gracefully
- **Verbatim code block preservation** — `<pre>` blocks are sheltered during extraction and restored as fenced code blocks in the final Markdown
- **Encoding auto-detection** — handles non-UTF-8 pages via HTTP headers, HTML meta tags, and `charset_normalizer`
- **Politeness delays** — configurable delay between requests to avoid overwhelming target servers
- **Structured output** — pages are organized with headings and separated by horizontal rules in the final document

## Installation

```bash
# Clone the repository
git clone https://github.com/example/html-to-markdown.git
cd html-to-markdown

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage — crawl and generate output/website.md
python main.py https://example.com/docs

# Specify output file
python main.py https://example.com/docs -o output/my_docs.md

# Limit crawl depth and page count
python main.py https://example.com/docs --max-depth 3 --max-pages 50

# Enable verbose (debug) logging
python main.py https://example.com/docs -v
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `URL` (arg) | Starting URL to crawl | *required* |
| `-o`, `--output` | Output Markdown file path | `output/website.md` |
| `--max-depth` | Maximum crawl depth | `5` |
| `--max-pages` | Maximum number of pages to crawl | `500` |
| `-v`, `--verbose` | Enable debug-level logging | `false` |

## Configuration

Settings are centralized in `config.py` and can be adjusted before running:

| Setting | Description | Default |
|---------|-------------|---------|
| `MAX_DEPTH` | Maximum crawl depth | `5` |
| `MAX_PAGES` | Maximum pages to process | `500` |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` |
| `REQUEST_RETRIES` | Retry count for failed requests | `3` |
| `REQUEST_DELAY` | Delay between requests (politeness) | `0.5` |
| `OUTPUT_DIR` | Default output directory | `output/` |
| `EXCLUDE_TAGS` | HTML tags to remove from content | `nav`, `header`, `footer`, `aside`, `script`, etc. |
| `EXCLUDE_CLASSES` | CSS classes that indicate non-content | `nav`, `sidebar`, `footer`, `cookie`, `ad-`, etc. |
| `PREFERRED_SELECTORS` | Priority order for content containers | `article`, `main`, `[role="main"]`, etc. |

## Project Structure

```
html-to-markdown/
├── main.py                  # CLI entry point (Typer)
├── config.py                # All configurable settings
├── requirements.txt         # Python dependencies
├── converter/
│   ├── __init__.py
│   └── markdown_converter.py   # HTML → Markdown (markdownify)
├── crawler/
│   ├── __init__.py
│   ├── crawler.py              # Core crawler (httpx + BeautifulSoup)
│   ├── link_extractor.py       # Internal link discovery
│   └── url_filter.py           # URL normalization & domain filtering
├── extractor/
│   ├── __init__.py
│   ├── content_extractor.py    # Multi-strategy content extraction
│   └── html_cleaner.py         # Tag/class/id-based HTML cleaning
├── merger/
│   ├── __init__.py
│   └── document_merger.py      # Merge pages into one Markdown doc
├── output/                     # Default output directory
└── tests/
    └── __init__.py
```

## How It Works

```text
User provides URL
        │
        ▼
Download HTML (httpx, with encoding detection)
        │
        ▼
Extract internal links (same domain, same protocol)
        │
        ▼
Visit subpages (BFS, respecting depth & page limits)
        │
        ▼
Clean HTML (remove nav, ads, scripts, etc.)
        │
        ▼
Extract content (trafilatura → readability → BS4 selectors)
        │
        ▼
Convert HTML → Markdown (markdownify, preserved <pre> blocks)
        │
        ▼
Merge documents (headings, horizontal rules, source URL)
        │
        ▼
Write final .md file
```

## Dependencies

| Package | Purpose |
|---------|---------|
| [httpx](https://www.python-httpx.org/) | HTTP client with async support |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) + [lxml](https://lxml.de/) | HTML parsing and traversal |
| [trafilatura](https://trafilatura.readthedocs.io/) | Primary content extraction engine |
| [readability-lxml](https://github.com/buriy/python-readability) | Fallback content extraction |
| [markdownify](https://github.com/matthewwithanm/python-markdownify) | HTML-to-Markdown conversion |
| [typer](https://typer.tiangolo.com/) | CLI framework |
| [rich](https://rich.readthedocs.io/) | Terminal formatting & progress display |

## License

MIT
