---
title: "Free JSON Schema Validator API: Validate JSON Against Any Schema"
published: false
tags: ["json", "api", "webdev", "validation"]
canonical_url: "https://toolpipe.dev"
---

Validating JSON against a schema shouldn't require installing libraries. Here's a free API that does it.

## ToolPipe JSON Schema Validator

```bash
curl -X POST https://toolpipe.dev/json/validate-schema \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {"type": "object", "required": ["name", "email"]},
    "data": {"name": "John", "email": "john@example.com"}
  }'
```

### Features
- Supports JSON Schema Draft 4, 6, 7, and 2020-12
- Detailed error messages with JSON Pointer paths
- Validates nested objects and arrays
- Custom format validators

### Also included: 120+ developer tools

JSON formatting, diff, merging, path querying, and 116 more tools. All free via REST API or MCP server.

```bash
npx @cosai-labs/toolpipe-mcp-server
```

[toolpipe.dev](https://toolpipe.dev)
