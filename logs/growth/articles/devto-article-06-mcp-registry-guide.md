# How to List Your MCP Server on Every Registry (2026 Guide)

The MCP (Model Context Protocol) ecosystem is exploding. 8M+ downloads, 85% month-over-month growth, and 11,000+ servers listed across registries. If you've built an MCP server, here's how to get it discovered.

## What is the MCP Registry?

The Official MCP Registry (registry.modelcontextprotocol.io) is the canonical source of truth for MCP servers. Other registries like PulseMCP, Glama, and mcp.so pull from it.

## Step 1: Create server.json

Every MCP server needs a `server.json` file following the official schema:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.yourorg/your-server",
  "title": "Your MCP Server",
  "description": "What your server does (under 100 chars)",
  "repository": {
    "url": "https://github.com/yourorg/your-repo",
    "source": "github"
  },
  "version": "1.0.0",
  "remotes": [
    {
      "type": "streamable-http",
      "url": "https://your-server.com/mcp"
    }
  ]
}
```

## Step 2: Install mcp-publisher

```bash
go install github.com/modelcontextprotocol/registry/cmd/mcp-publisher@latest
```

## Step 3: Authenticate and Publish

```bash
mcp-publisher login github
mcp-publisher publish server.json
```

That's it. Your server is now on the Official Registry.

## Step 4: Get Listed Everywhere

Once you're on the Official Registry, these aggregators pick you up automatically:
- **PulseMCP** (pulsemcp.com) - 11,000+ servers, ingests weekly
- **Glama** (glama.ai/mcp/servers) - 10,000+ servers

For manual submissions:
- **mcpservers.org** - Free listing, web form
- **mcp.so** - Requires Google login
- **Smithery.ai** - CLI-based, requires API key

## Step 5: Submit to Awesome Lists

The biggest awesome-mcp-servers lists on GitHub:
- wong2/awesome-mcp-servers (fork, add entry, PR)
- appcypher/awesome-mcp-servers
- TensorBlock/awesome-mcp-servers

## Real Example: ToolPipe

ToolPipe (238+ developer tools) is listed on the Official Registry as `io.github.COSAI-Labs/toolpipe-mcp-server`. You can add it to Claude Code:

```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://toolpipe.dev/mcp"
    }
  }
}
```

Tools include JSON formatting, QR codes, hash generation, UUID, DNS lookup, WHOIS, PDF generation, text analysis, image processing, code review, and 220+ more. No API key required.

- [Official Registry](https://registry.modelcontextprotocol.io)
- [GitHub](https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server)

---

*Tags: mcp, claude, ai, devtools*
