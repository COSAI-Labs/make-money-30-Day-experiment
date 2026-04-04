---
title: "Free HTML to Markdown Converter API"
published: false
tags: api, webdev, markdown, tools
---

Convert between HTML and Markdown programmatically. ToolPipe's free API handles both directions.

## Markdown to HTML

```bash
curl -X POST "https://toolpipe.dev/markdown/to-html" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold**."}'
```

## Features

- Bidirectional conversion
- GFM (GitHub Flavored Markdown) support
- Tables, code blocks, lists
- No auth required, free tier

[Explore ToolPipe](https://toolpipe.dev) - 55+ free developer APIs.
