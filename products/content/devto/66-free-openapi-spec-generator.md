---
title: "Free OpenAPI Spec Generator API: From Description to Documentation"
published: false
tags: openapi, documentation, api, devtools
---

Generate OpenAPI/Swagger specifications from API descriptions.

```bash
curl -X POST https://toolpipe.dev/openapi/generate \
  -H "Content-Type: application/json" \
  -d '{"name": "My API", "endpoints": [{"path": "/users", "method": "GET", "description": "List users"}]}'
```

Free, no signup. [Docs](https://toolpipe.dev/docs) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
