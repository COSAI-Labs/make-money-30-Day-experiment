---
title: "Free Code Minifier API: Minify CSS, JS, and HTML via REST"
published: false
tags: css, javascript, optimization, api
---

Minify your code via API without build tools. ToolPipe's code minifier handles CSS, JavaScript, and HTML.

## Endpoints

- `POST /api/css/minify` - Minify CSS
- `POST /api/js/minify` - Minify JavaScript
- `POST /api/html/minify` - Minify HTML

## Example

```bash
curl -X POST https://toolpipe.dev/api/css/minify \
  -H "Content-Type: application/json" \
  -d '{"code": "body { margin: 0; padding: 0; }"}'
```

Returns minified code with size reduction stats.

**Try it**: [toolpipe.dev](https://toolpipe.dev) - 240+ free developer APIs.
