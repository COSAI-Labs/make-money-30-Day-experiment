---
title: "Free Markdown to HTML API: Convert Docs Programmatically"
published: false
tags: markdown, html, api, webdev
---

Convert Markdown to clean HTML via REST API. Perfect for CMS and documentation pipelines.

```bash
curl -X POST https://toolpipe.dev/markdown/to-html \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold** text."}'
```

GFM support, code highlighting, table support, XSS sanitization.

[ToolPipe](https://toolpipe.dev) - free developer tools API.
