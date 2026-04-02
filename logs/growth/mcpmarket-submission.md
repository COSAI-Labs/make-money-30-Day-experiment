# MCP Market Submission (mcpmarket.com)

## Status: BLOCKED - GitHub API rate limit / invalid token

## Submission Method
mcpmarket.com is run by CherryHQ. Submissions are done by creating GitHub issues at:
https://github.com/CherryHQ/mcpmarket/issues

The site itself (mcpmarket.com) is protected by Vercel bot protection and cannot be accessed via curl/automated tools.

## Direct Link to Create Issue
https://github.com/CherryHQ/mcpmarket/issues/new?title=Add+ToolPipe+MCP+Server%3A+120%2B+developer+tools+for+AI+agents

## Issue Title
Add ToolPipe MCP Server: 120+ developer tools for AI agents

## Issue Body

**Name**: ToolPipe MCP Server
**GitHub**: https://github.com/nicholasrossi0530/toolpipe-mcp-server
**npm**: @cosai-labs/toolpipe-mcp-server
**Description**: 120+ developer tools as MCP tools for AI agents. JSON formatter, QR generator, hash tools, PDF tools, SSL checker, DNS lookup, WHOIS, regex tester, JWT decoder, and more. Available as both an npm package and a remote HTTP MCP endpoint.
**Category**: Developer Tools / Utilities
**Remote Endpoint**: https://troops-submission-what-stays.trycloudflare.com/mcp

### Tools (120+)

Includes tools across these categories:

- **Encoding/Decoding**: Base64, URL encode/decode, JWT decoder, HTML entities
- **Hashing**: MD5, SHA-1, SHA-256, SHA-512, bcrypt
- **Formatters**: JSON formatter/validator, XML formatter, SQL formatter, CSS/JS minifier
- **Network**: DNS lookup, WHOIS, SSL checker, HTTP headers, ping, port scanner
- **Generators**: QR code, UUID, password, lorem ipsum, color palette
- **Converters**: Unit converter, number base converter, timestamp converter, markdown to HTML
- **Text Tools**: Regex tester, diff checker, word counter, case converter, slug generator
- **PDF Tools**: PDF generation, text extraction
- **Dev Utilities**: Cron expression parser, user agent parser, IP geolocation, HTTP status codes

### Installation

```bash
npx @cosai-labs/toolpipe-mcp-server
```

Or add to your MCP client config:

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

Or use the remote HTTP endpoint:

```json
{
  "mcpServers": {
    "toolpipe": {
      "type": "url",
      "url": "https://troops-submission-what-stays.trycloudflare.com/mcp"
    }
  }
}
```

### Links

- Repository: https://github.com/nicholasrossi0530/toolpipe-mcp-server
- npm: https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server
- License: MIT
