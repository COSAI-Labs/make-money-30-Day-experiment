# PulseMCP Submission Notes

## Status
- Email delivery failed: both hi@pulsemcp.com and submit@pulsemcp.com bounce (Google says accounts don't exist)
- Web form at https://pulsemcp.com/submit is behind Cloudflare protection
- PulseMCP also ingests from Official MCP Registry (modelcontextprotocol/registry) daily

## Recommended Actions
1. Use PulseMCP web form manually at https://pulsemcp.com/submit
   - Select "MCP Server"
   - URL: https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server
2. Publish to Official MCP Registry via `mcp-publisher` (requires interactive GitHub device auth)
   - Run: `mcp-publisher login github` and complete device auth
   - Then: `mcp-publisher publish products/mcp-server/server.json`
   - PulseMCP will auto-ingest from the official registry

## Email Draft (saved at logs/pulsemcp-email.eml)
From: toolpipe-ads@sharebot.net
To: submit@pulsemcp.com (bounced) / hi@pulsemcp.com (bounced)
Subject: Listing Request: ToolPipe MCP Server (139+ Developer Tools)
