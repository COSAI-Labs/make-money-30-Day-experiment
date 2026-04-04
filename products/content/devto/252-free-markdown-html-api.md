---
title: "Free Markdown to HTML Converter API"
tags: markdown, html, api, webdev
canonical_url: https://toolpipe.dev
---

Convert Markdown to clean HTML with a single API call. GitHub Flavored Markdown support.

## Usage

```bash
curl -X POST https://toolpipe.dev/markdown/to-html \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold**"}'
```

Supports tables, code blocks, task lists, and more.

**Try it:** [toolpipe.dev](https://toolpipe.dev)
