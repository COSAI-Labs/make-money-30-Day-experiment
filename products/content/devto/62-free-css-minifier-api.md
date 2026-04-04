---
title: "Free CSS Minifier API: Optimize Stylesheets Programmatically"
published: false
tags: css, performance, api, webdev
---

Minify CSS in your build pipeline via REST API.

```bash
curl -X POST https://toolpipe.dev/css/minify \
  -H "Content-Type: application/json" \
  -d '{"css": "body { margin: 0; padding: 0; }"}'
```

Removes whitespace, comments, and optimizes selectors. Free, no signup. Part of ToolPipe's 120+ developer tools.

[API docs](https://toolpipe.dev/docs) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
