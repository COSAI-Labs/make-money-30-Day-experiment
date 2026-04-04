---
title: "Minify JavaScript, CSS, and HTML via API (No Build Step)"
published: false
tags: javascript, css, webdev, performance
canonical_url: https://toolpipe.dev
---

Need to minify code without setting up a build pipeline? ToolPipe's code minification API handles JS, CSS, and HTML via simple REST calls.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/code/minify \
  -H "Content-Type: application/json" \
  -d '{"code": "function hello() {\n  return 42;\n}", "language": "javascript"}'
```

## Supported Languages

| Language | What It Does |
|----------|-------------|
| JavaScript | Variable renaming, dead code elimination |
| CSS | Property merging, shorthand conversion |
| HTML | Whitespace removal, attribute optimization |

## Use Cases

- Quick minification without webpack/rollup
- CI/CD pipeline step via curl
- On-demand minification in serverless functions

## 55+ More Tools

ToolPipe has 55+ free API endpoints and 238 MCP tools for AI agents.

- **API**: [toolpipe.dev](https://toolpipe.dev)
- **MCP**: `npx @cosai-labs/toolpipe-mcp-server`
- **npm**: [@cosai-labs/toolpipe-mcp-server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
