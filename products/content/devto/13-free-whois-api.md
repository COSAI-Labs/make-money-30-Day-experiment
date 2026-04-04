---
title: "Free WHOIS Lookup API: Domain Registration Data Without Signup"
published: false
tags: ["api", "devops", "webdev", "tools"]
canonical_url: "https://toolpipe.dev"
---

## The Problem

You need domain registration data in your app or script. Most WHOIS APIs require signup, API keys, and have strict rate limits. What if you just need a quick lookup?

## The Solution: ToolPipe WHOIS API

ToolPipe provides a free WHOIS lookup API. No signup, no API key, just curl and go.

```bash
curl "https://toolpipe.dev/whois/lookup?domain=github.com"
```

### What You Get Back

- **Registrar**: The company managing the domain
- **Created/Updated/Expires**: Full date timeline
- **Nameservers**: All NS records
- **Status codes**: clientDeleteProhibited, etc.
- **DNSSEC**: Signed or unsigned

## But Wait, There's 119 More

WHOIS is just one of 120+ endpoints. Here are some others:

| Endpoint | What it does |
|----------|-------------|
| `/dns/lookup?domain=` | Full DNS records (A, MX, NS, TXT) |
| `/ssl/check?domain=` | SSL certificate details and expiry |
| `/security/headers?url=` | HTTP security header analysis |
| `/qr/generate` | Generate QR codes as PNG |
| `/hash/generate` | MD5, SHA256, SHA512 |
| `/jwt/decode` | Decode JWT tokens |
| `/sql/format` | Beautify SQL queries |

## For AI Coding Agents

All 120+ tools are also available as an MCP server:

```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://toolpipe.dev/mcp"
    }
  }
}
```

Works with Claude, Cursor, Windsurf, VS Code, Cline.

**npm**: `npx @cosai-labs/toolpipe-mcp-server`

## Links

- [ToolPipe Website](https://toolpipe.dev)
- [GitHub](https://github.com/COSAI-Labs/toolpipe-mcp-server)
- [npm](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
