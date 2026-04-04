---
title: "Free Code Formatting API: Format Any Language via REST"
published: false
tags: coding, api, devtools, formatting
---

Format code in 10+ languages with a single API call. No Prettier config needed.

```bash
curl -X POST https://toolpipe.dev/code/format \
  -H "Content-Type: application/json" \
  -d '{"code": "const x={a:1,b:2}", "language": "javascript"}'
```

## Supported Languages
- JavaScript / TypeScript
- Python
- HTML / CSS
- JSON / YAML / XML
- SQL
- Markdown

## Use Cases
- CI/CD formatting checks
- Editor extensions
- Documentation generators
- Code snippet formatters

Free at [toolpipe.dev](https://toolpipe.dev). Also available as MCP server: `npx @cosai-labs/toolpipe-mcp-server`
