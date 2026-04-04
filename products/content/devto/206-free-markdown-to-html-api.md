---
title: "Free Markdown to HTML Converter API: GFM Support via REST"
published: false
tags: ["api", "markdown", "webdev", "productivity"]
canonical_url: "https://toolpipe.dev"
---

# Free Markdown to HTML Converter API

Convert Markdown to HTML via REST. Supports GitHub Flavored Markdown including tables and task lists.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/markdown/to-html \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold** text."}'
```

## Supported Features

- Headers, paragraphs, lists
- Bold, italic, strikethrough
- Code blocks with syntax highlighting
- Tables (GFM)
- Links and images
- Task lists

## Use Cases

- CMS rendering pipelines
- Email template generation from markdown
- Documentation site builds
- Blog post processing

[https://toolpipe.dev](https://toolpipe.dev) - 120+ free developer APIs
