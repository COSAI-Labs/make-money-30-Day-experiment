---
title: "Free CSS Minifier API for Build Pipelines"
published: false
tags: ["api", "css", "performance", "webdev"]
---

## Free CSS Minifier API

Minify CSS via API. Integrate into build pipelines, CI/CD, or any workflow.

### Endpoint

```
POST https://toolpipe.dev/api/css/minify
```

### Request Body

```json
{
  "css": "body {\n  margin: 0;\n  padding: 0;\n  font-family: Arial, sans-serif;\n}"
}
```

### What It Does

- Removes whitespace and comments
- Shortens color values where possible
- Reduces overall CSS file size
- Returns minified output as JSON

### Example

```bash
curl -X POST https://toolpipe.dev/api/css/minify \
  -H "Content-Type: application/json" \
  -d '{"css": "body { margin: 0; padding: 0; }"}'
```

No signup. No rate limits for basic use. Part of 70+ tools at [toolpipe.dev](https://toolpipe.dev).
