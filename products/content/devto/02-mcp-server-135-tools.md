---
title: "I Built an MCP Server with 135+ Tools for AI Coding Assistants"
published: false
description: "How I packaged 135+ developer utilities into a single MCP server that works with Claude, Cursor, Windsurf, and any MCP-compatible AI assistant."
tags: mcp, ai, developer-tools, claude
cover_image: 
canonical_url: https://toolpipe.dev
---

If you're using Claude Desktop, Cursor, or Windsurf, you already know the power of MCP (Model Context Protocol) servers. They give your AI assistant access to external tools and data.

I built **ToolPipe**, an MCP server that bundles 135+ developer utilities into one package. Here's what it does and how to use it.

## The Problem

Every developer has a scattered collection of bookmarked tools: a JSON formatter here, a regex tester there, a JWT decoder somewhere else. When you're in the middle of coding with an AI assistant, you have to context-switch to use these tools.

## The Solution

One MCP server. 135+ tools. Zero setup friction.

```bash
npx @cosai-labs/toolpipe-mcp-server
```

Add it to your Claude Desktop config:

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["-y", "@cosai-labs/toolpipe-mcp-server"]
    }
  }
}
```

## What's Included

### Code Tools
- **code_review**: Get AI-powered code review for bugs, security issues, and best practices
- **code_explain**: Explain any code snippet in plain English
- **code_format**: Format code in 20+ languages
- **generate_regex**: Describe what you want in English, get a regex pattern
- **json_to_typescript**: Paste JSON, get TypeScript interfaces

### DevOps Tools
- **generate_dockerfile**: Generate production-ready Dockerfiles for any stack
- **generate_docker_compose**: Multi-service Docker Compose configs
- **parse_cron**: Human-readable cron expression parsing
- **ssl_check**: Inspect SSL certificates
- **dns_lookup**: DNS records for any domain

### Data & Conversion
- **json_format**: Format, validate, minify JSON
- **csv_to_json**: Convert CSV data to JSON
- **base64**: Encode/decode Base64
- **convert_timestamp**: Unix timestamps to ISO and back
- **convert_color**: HEX, RGB, HSL color conversion

### Security
- **generate_hash**: MD5, SHA-1, SHA-256, SHA-512
- **jwt_decode** / **jwt_create**: Full JWT operations
- **generate_password**: Cryptographically strong passwords
- **whois_lookup**: Domain registration info

### Web Tools
- **generate_qr_code**: QR code generation
- **shorten_url**: URL shortener
- **web_extract**: Pull structured content from any URL
- **http_headers**: Inspect response headers

## Real Usage Example

With ToolPipe connected, you can ask Claude things like:

> "Check the SSL certificate for api.example.com"

> "Generate a Dockerfile for a Node.js 20 app with PostgreSQL"

> "Review this function for security issues" (paste code)

> "Convert this CSV to JSON" (paste CSV data)

The AI assistant calls the appropriate ToolPipe tool and gives you the result inline, no tab switching.

## Also a REST API

Every tool is also available as a REST API at [toolpipe.dev/docs](https://toolpipe.dev/docs). No signup, no API key needed for basic usage.

```bash
# Format JSON
curl -X POST https://toolpipe.dev/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"name\":\"test\"}"}'

# Generate a QR code
curl "https://toolpipe.dev/api/qr?text=https://example.com"

# DNS lookup
curl "https://toolpipe.dev/api/dns/lookup?domain=github.com"
```

## Try It

- Website: [toolpipe.dev](https://toolpipe.dev)
- GitHub: [COSAI-Labs/toolpipe](https://github.com/COSAI-Labs/toolpipe)
- MCP Setup: `npx @cosai-labs/toolpipe-mcp-server`

All 135+ tools are free. No signup needed.

What tools would you want added? Let me know in the comments.
