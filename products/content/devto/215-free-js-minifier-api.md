---
title: "Free JavaScript Minifier API"
published: false
tags: ["api", "javascript", "performance", "webdev"]
---

## Free JavaScript Minifier API

Minify JavaScript code via REST API. Perfect for build automation and CI/CD pipelines.

### Endpoint

```
POST https://toolpipe.dev/api/js/minify
```

### Request Body

```json
{
  "code": "function hello(name) {\n  console.log('Hello, ' + name);\n}\nhello('World');"
}
```

### Features

- Whitespace removal
- Variable shortening
- Dead code elimination
- JSON API with CORS

### Example

```bash
curl -X POST https://toolpipe.dev/api/js/minify \
  -H "Content-Type: application/json" \
  -d '{"code": "function add(a, b) { return a + b; }"}'
```

Free at [toolpipe.dev](https://toolpipe.dev). 70+ developer tools, zero signup.
