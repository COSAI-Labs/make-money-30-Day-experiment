---
title: "Free API Client Code Generator from OpenAPI Specs"
published: false
tags: api, openapi, typescript, webdev
---

## Generate API Clients from Swagger/OpenAPI

Feed your OpenAPI spec to ToolPipe and get typed API client code in TypeScript, Python, Go, or Rust.

### Quick Start

```bash
curl -X POST https://toolpipe.dev/generate/api-client \
  -H "Content-Type: application/json" \
  -d '{"spec_url": "https://petstore.swagger.io/v2/swagger.json", "language": "typescript"}'
```

### Supported Languages

- TypeScript with full type safety
- Python with type hints
- Go with struct generation
- Rust with serde support

### MCP Server

AI agents can use this tool directly:
```bash
npx @cosai-labs/toolpipe-mcp-server
```

[toolpipe.dev](https://toolpipe.dev) | [npm](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
