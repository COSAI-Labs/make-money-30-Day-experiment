---
title: "Free SQL Formatter API: Beautify Queries via REST"
published: false
tags: ["sql", "api", "database", "webdev"]
canonical_url: "https://toolpipe.dev"
---

## Stop Manually Formatting SQL

We've all been there: a 200-character single-line SQL query that's impossible to read. Most formatters require a browser visit. Here's one that works from your terminal.

## ToolPipe SQL Formatter

```bash
curl -X POST https://toolpipe.dev/sql/format \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT u.id,u.name,o.total FROM users u JOIN orders o ON u.id=o.user_id WHERE o.total>100 ORDER BY o.total DESC"}'
```

Returns beautifully formatted SQL with proper indentation, keyword capitalization, and line breaks.

## Use Cases

- **CI/CD pipelines**: Auto-format SQL migrations before commit
- **Code review**: Format SQL in PR comments for readability
- **Documentation**: Generate readable SQL for docs
- **Learning**: See proper SQL formatting patterns

## 120+ More Dev Tools

ToolPipe isn't just SQL formatting. It's 120+ developer utility APIs:

- JSON formatting and validation
- Code minification (JS/CSS/HTML)
- Regex testing
- DNS/WHOIS/SSL lookups
- QR code generation
- UUID generation
- JWT decoding
- And 100+ more

## MCP Server for AI Agents

```json
{
  "mcpServers": {
    "toolpipe": { "url": "https://toolpipe.dev/mcp" }
  }
}
```

## Links

- [ToolPipe](https://toolpipe.dev) | [GitHub](https://github.com/COSAI-Labs/toolpipe-mcp-server) | [npm](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
