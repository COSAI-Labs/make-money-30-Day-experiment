# MCP Registry Submissions - Session 98
Date: 2026-04-03

## Summary
Submitted ToolPipe MCP Server to MCP registries and directories.

## Successful Submissions

### 1. Official MCP Registry (registry.modelcontextprotocol.io)
- **Status**: PUBLISHED
- **Method**: REST API (POST /v0.1/publish with GitHub OAuth JWT)
- **Server name**: io.github.GerritRoska/toolpipe-mcp-server
- **Version**: 1.0.0
- **URL**: https://registry.modelcontextprotocol.io (searchable)
- **Published at**: 2026-04-03T19:11:56Z
- **Details**: Registered with SSE remote transport pointing to Cloudflare tunnel

### 2. awesome-mcp-servers (punkpeye/awesome-mcp-servers)
- **Status**: PR SUBMITTED
- **PR**: https://github.com/punkpeye/awesome-mcp-servers/pull/4088
- **Method**: GitHub PR from fork (GerritRoska/awesome-mcp-servers-4)
- **Section**: Developer Tools (alphabetically placed)
- **Note**: This repo feeds mcpservers.org and Glama's directory. Once merged, ToolPipe will appear on both.

## Blocked (Browser-Only Submissions)

### 3. PulseMCP (pulsemcp.com)
- **Status**: BLOCKED (Cloudflare WAF blocks curl/API access)
- **Action**: Gmail draft created to submit@pulsemcp.com
- **Draft ID**: r8689877663897321213

### 4. Smithery.ai
- **Status**: BLOCKED (requires API key from web dashboard)
- **Method attempted**: smithery mcp publish CLI (requires interactive auth)
- **Action**: Gmail draft created to hello@smithery.ai
- **Draft ID**: r1707702179954673860

### 5. Glama (glama.ai/mcp/servers)
- **Status**: PENDING (auto-indexes from awesome-mcp-servers PR)
- **Action**: Gmail draft created to support@glama.ai as backup
- **Draft ID**: r3045021142285386210
- **Note**: Glama is run by same maintainer as awesome-mcp-servers. PR #4088 should auto-populate.

### 6. mcp.so
- **Status**: BLOCKED (no public API or submission endpoint found)
- **Note**: mcp.so appears to auto-index from GitHub. The /submit endpoint returns 404. May auto-discover once the awesome-mcp-servers PR merges.

### 7. mcpmarket.com
- **Status**: BLOCKED (returns 403 Forbidden on all requests)
- **Note**: Site may be down or behind strict auth.

### 8. modelcontextprotocol/servers (official reference repo)
- **Status**: NOT APPLICABLE
- **Note**: This repo only houses reference implementations maintained by the MCP steering group. Community servers should use the MCP Registry (which we already published to).

## Total Results
- 1 successful API publication (Official MCP Registry)
- 1 PR submitted (awesome-mcp-servers, which feeds 2+ directories)
- 3 email drafts created for browser-only registries
- 2 registries blocked/not applicable
