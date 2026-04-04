---
title: "How to Add 238 Developer Tools to Your AI Coding Agent in 30 Seconds"
published: false
description: "Give Claude, Cursor, or Windsurf access to QR codes, JSON formatting, DNS lookups, and 235 more tools via one MCP server."
tags: ai, mcp, claude, devtools
cover_image: 
canonical_url: https://github.com/COSAI-Labs/toolpipe-mcp-server
---

## The Setup

AI coding agents like Claude Code, Cursor, and Windsurf support MCP (Model Context Protocol) servers. These servers give agents access to external tools.

**ToolPipe MCP Server** provides 238 developer utility tools your agent can call:

```bash
npx -y @cosai-labs/toolpipe-mcp-server
```

## What Your Agent Gets

After connecting, your AI agent can:

- **Generate QR codes** from URLs or text
- **Format JSON/XML/YAML** with proper indentation
- **Look up DNS records** for any domain
- **Decode JWT tokens** to inspect claims
- **Generate UUIDs** in v1/v4/v5 formats
- **Compute hashes** (MD5, SHA-256, SHA-512)
- **Check SSL certificates** for expiry
- **Analyze SEO** for any website
- **Convert between formats** (Markdown to HTML, CSV to JSON, etc.)
- And 229 more tools...

## Configuration

### Claude Code / Claude Desktop

Add to your MCP config:

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

### Cursor

Add to `.cursor/mcp.json`:

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

## Why This Matters

Without MCP tools, AI agents can only read and write code. With ToolPipe, they can interact with the real world: check DNS, validate certificates, generate assets, and more.

**GitHub:** [COSAI-Labs/toolpipe-mcp-server](https://github.com/COSAI-Labs/toolpipe-mcp-server)
**npm:** [@cosai-labs/toolpipe-mcp-server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
