---
title: "Free Code Review API - Automated Quality Checks for Any Language"
published: false
tags: webdev, api, codequality, devtools
---

## Automated Code Review via API

ToolPipe offers a free Code Review API that analyzes your code for quality issues, complexity metrics, and improvement suggestions.

### Quick Start

```bash
curl -X POST https://toolpipe.dev/code/review \
  -H "Content-Type: application/json" \
  -d '{"code": "function add(a,b){return a+b}", "language": "javascript"}'
```

### What You Get

- Cyclomatic complexity scoring
- Code smell detection
- Best practice suggestions
- Maintainability index
- Support for JavaScript, TypeScript, Python, and more

### MCP Server for AI Agents

```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://troops-submission-what-stays.trycloudflare.com/mcp"
    }
  }
}
```

**Free tier**: 100 calls/day with email-only API key.

[Full docs](https://toolpipe.dev/docs) | [npm](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
