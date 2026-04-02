---
title: "I Built a 230-Endpoint API and Turned It Into an MCP Server. Here's What Happened."
published: false
tags: webdev, api, ai, showdev
canonical_url: https://assessing-scoop-authorities-sheet.trycloudflare.com
---

Last week I shipped ToolPipe: a single API with 230+ developer utility endpoints. JSON formatting, QR codes, hashing, DNS lookup, code review, fake data generation, Dockerfile creation, and more.

Then I wrapped 45 of the most useful endpoints as an MCP (Model Context Protocol) server so AI agents could use them.

## The API

Built with FastAPI (Python). Single file, ~10,000 lines. Every endpoint is self-contained with no external dependencies beyond the standard library + a few packages.

Some highlights:

```bash
# Format JSON
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/json/format \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"name\":\"test\"}"}'

# Generate QR Code
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=hello&size=300"

# DNS Lookup
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/dns/lookup?domain=google.com"

# Check if site is down
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/down/check?url=https://github.com"

# Get crypto prices
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/crypto/prices?coins=btc,eth,sol"

# Generate fake data
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/data/fake \
  -H "Content-Type: application/json" \
  -d '{"type": "person", "count": 5}'
```

All endpoints return JSON. Free tier: 100 calls/day, no signup.

## The MCP Server

MCP is the new standard for connecting AI models to tools. Claude Desktop, Cursor, Windsurf, and other AI tools support it natively.

I wrapped 45 of the most useful endpoints into an npm package:

```bash
npx -y @cosai-labs/toolpipe-mcp-server
```

One command. Add it to your AI tool's MCP config and your agent can:
- Format and validate JSON
- Generate QR codes, UUIDs, passwords
- Look up DNS records, check SSL certificates
- Review code for bugs and security issues
- Generate Dockerfiles and docker-compose files
- Make HTTP requests to any URL
- Analyze websites for SEO
- Generate TypeScript interfaces from JSON
- And 37 more tools

## What I Learned

**1. Agents need tools more than humans do.** Humans can open a browser tab. Agents can't. An HTTP request proxy tool is boring for a human API but transformative for an agent.

**2. MCP is growing fast.** 8M+ downloads, 85% MoM growth. The ecosystem is hungry for useful servers.

**3. Free tiers drive adoption.** 100 calls/day costs almost nothing to serve but removes all friction. Users who hit the limit are already hooked.

**4. Packaging matters.** The same API exposed as raw REST endpoints got modest interest. Packaged as "45 MCP tools you can add in 30 seconds" got 10x more engagement.

## Try It

- **API Docs**: [assessing-scoop-authorities-sheet.trycloudflare.com/docs](https://assessing-scoop-authorities-sheet.trycloudflare.com/docs)
- **MCP Server**: `npx -y @cosai-labs/toolpipe-mcp-server`
- **Postman Collection**: [Download](https://assessing-scoop-authorities-sheet.trycloudflare.com/postman)
- **GitHub**: [COSAI-Labs/make-money-30day-challenge](https://github.com/COSAI-Labs/make-money-30day-challenge)

What tools would you want added? I'm building in public and shipping fast.
