---
title: "Free CSS Minifier API - Optimize Stylesheets Programmatically"
published: false
tags: ["api", "css", "webdev", "performance"]
---

Minify CSS files programmatically with ToolPipe's free CSS Minifier API. Reduce file sizes and improve page load times.

## API Endpoint

```
POST https://toolpipe.dev/api/css/minify
Content-Type: application/json

{"code": "body {\n  margin: 0;\n  padding: 0;\n}"}

Response:
{"minified": "body{margin:0;padding:0}", "original_size": 35, "minified_size": 22, "savings": "37%"}
```

Also available: JavaScript minification at `/api/js/minify`.

Part of 70+ free developer tools at [toolpipe.dev](https://toolpipe.dev). No signup required.
