---
title: "Free MCP Server with 120+ Developer Tools for AI Agents"
published: false
tags: ["mcp", "ai", "devtools", "api"]
canonical_url: "https://toolpipe.dev"
---

## ToolPipe MCP Server

If you're building with AI agents (Claude, Cursor, Windsurf, Cline, VS Code), you need tools. ToolPipe gives you 120+ developer utilities via MCP (Model Context Protocol) with zero install.

### Quick Start

Add to your Claude Desktop or Claude Code config:

```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://troops-submission-what-stays.trycloudflare.com/mcp"
    }
  }
}
```

Or via npx:

```bash
npx @cosai-labs/toolpipe-mcp-server
```

### What's Included

- **Code tools**: Review, formatting, minification, linting
- **Data tools**: JSON/XML/YAML/CSV conversion, fake data generation
- **DevOps tools**: Docker Compose, GitHub Actions, Nginx config generation
- **Security tools**: SSL checker, security headers, WHOIS lookup
- **Text tools**: Summarization, keyword extraction, sentiment analysis
- **Generators**: QR codes, UUIDs, hashes, TypeScript types, API clients

No API key needed for the free tier (100 calls/day).

- [Website](https://toolpipe.dev)
- [npm](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
- [GitHub](https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server)
