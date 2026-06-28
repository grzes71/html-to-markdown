# AI_CONTEXT.md

## Project Overview

**Project Name:** html-to-markdown

The goal of this project is to create a Python command-line application that crawls a website starting from a given URL, collects content from the main page and selected subpages, and generates a single consolidated Markdown document.

The resulting Markdown file should contain only meaningful textual content and basic document structure. Navigation menus, advertisements, cookie banners, footers, sidebars, tracking elements, and other non-content elements should be removed whenever possible.

---

## Main Objectives

1. Accept a starting URL from the user.
2. Download and parse the HTML content of the page.
3. Discover and follow internal links belonging to the same website.
4. Recursively process selected subpages.
5. Extract meaningful content from each page.
6. Convert extracted content into Markdown format.
7. Merge all collected content into a single Markdown file.
8. Preserve logical document structure and page hierarchy.

---

## Expected Workflow

```text
User provides URL
        │
        ▼
Download HTML
        │
        ▼
Extract internal links
        │
        ▼
Visit subpages
        │
        ▼
Extract article/content sections
        │
        ▼
Convert HTML → Markdown
        │
        ▼
Merge documents
        │
        ▼
Generate final .md file
```

---

## Functional Requirements

### URL Input

The application should support:

* Single URL provided via command line
* Future support for configuration files

Example:

```bash
python main.py https://example.com/docs
```

---

### Crawling

The crawler should:

* Stay within the same domain
* Avoid external links
* Avoid duplicate page processing
* Respect configurable depth limits
* Respect configurable page limits

Example configuration:

```python
MAX_DEPTH = 5
MAX_PAGES = 500
```

---

### Content Extraction

The extractor should prioritize:

* article
* main
* documentation content containers
* markdown-like content areas

The extractor should ignore:

* navigation menus
* headers
* footers
* sidebars
* cookie banners
* advertisements
* scripts
* styles
* tracking elements

Preferred libraries:

* BeautifulSoup
* readability-lxml
* trafilatura

---

### Markdown Conversion

HTML should be converted into clean Markdown.

Supported elements:

* headings
* paragraphs
* lists
* tables
* code blocks
* inline code
* blockquotes
* links
* images (optional)

Preferred libraries:

* markdownify
* html2text

---

### Document Merging

The generated document should preserve page boundaries.

Example:

```markdown
# Example Documentation

## Introduction

Content from first page...

---

## Installation

Content from second page...

---

## Configuration

Content from third page...
```

---

## Output Requirements

The generated Markdown should:

* Be human-readable
* Be LLM-friendly
* Preserve heading hierarchy
* Avoid duplicate content
* Use UTF-8 encoding
* Produce deterministic output whenever possible

Output file example:

```text
output/
└── website.md
```

---

## Non-Functional Requirements

### Performance

* Handle hundreds of pages
* Avoid excessive memory usage
* Support streaming where possible

### Reliability

* Handle network failures gracefully
* Retry failed requests
* Continue processing when individual pages fail

### Logging

Provide structured logging:

```text
INFO    Crawling page ...
INFO    Extracted content ...
WARNING Failed to process page ...
ERROR   Network error ...
```

---

## Suggested Project Structure

```text
html-to-markdown/
│
├── main.py
├── config.py
├── requirements.txt
├── AI_CONTEXT.md
│
├── crawler/
│   ├── crawler.py
│   ├── url_filter.py
│   └── link_extractor.py
│
├── extractor/
│   ├── content_extractor.py
│   └── html_cleaner.py
│
├── converter/
│   └── markdown_converter.py
│
├── merger/
│   └── document_merger.py
│
├── output/
│
└── tests/
```

---

## Suggested Technology Stack

### Core

* Python 3.12+

### Networking

* requests
* httpx

### Parsing

* BeautifulSoup4
* lxml

### Content Extraction

* trafilatura
* readability-lxml

### Markdown Conversion

* markdownify

### CLI

* argparse
* typer

### Testing

* pytest

---

## Future Features

### Phase 2

* Sitemap.xml support
* robots.txt support
* Parallel crawling
* Incremental updates
* Multiple output files

### Phase 3

* PDF generation
* DOCX generation
* AI-assisted content cleanup
* Automatic table of contents
* Website change detection

---

## Coding Standards

* Use type hints everywhere.
* Follow PEP 8.
* Prefer composition over inheritance.
* Write unit tests for all core modules.
* Keep modules small and focused.
* Avoid global state when possible.

---

## AI Assistant Instructions

When generating code for this project:

1. Prefer simple and maintainable solutions.
2. Use type annotations.
3. Add docstrings for public functions.
4. Avoid unnecessary abstractions.
5. Favor readability over cleverness.
6. Keep dependencies minimal.
7. Ensure code works on Linux, macOS, and Windows.
8. Generate production-quality code whenever possible.
9. Include error handling and logging.
10. Assume that the resulting Markdown may later be consumed by LLM systems for Retrieval-Augmented Generation (RAG) workflows.

---

## Success Criteria

The project is considered successful when:

* A user provides a website URL.
* The application crawls the site.
* Relevant content is extracted from pages and subpages.
* A single clean Markdown document is generated.
* The document can be easily read by humans and AI systems.
