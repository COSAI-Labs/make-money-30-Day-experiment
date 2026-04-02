# Growth: Session 49 - MCP Registry Submissions

Date: 2026-04-02
Agent: Growth

## Objective
Submit ToolPipe MCP Server to all major MCP registries and directories.

## Results by Registry

### 1. Awesome MCP Servers (punkpeye/awesome-mcp-servers) - PR CREATED
- Closed 3 old PRs (#3955, #3969, #3977) that had "missing-glama" labels or were outdated
- Created new PR #3995 with Glama badge included: https://github.com/punkpeye/awesome-mcp-servers/pull/3995
- Entry includes 238+ tools description, Glama badge, npm install command, and remote MCP URL
- Status: OPEN, awaiting review

### 2. Awesome MCP List (MobinX/awesome-mcp-list) - PR ALREADY OPEN
- PR #166 already submitted: https://github.com/MobinX/awesome-mcp-list/pull/166
- Status: OPEN

### 3. Glama.ai - ALREADY LISTED
- ToolPipe is already indexed on Glama at: https://glama.ai/mcp/servers/Aldric-Core/toolpipe-mcp-server
- Auto-discovered from GitHub/npm
- Shows as "Developer Tools, Code Execution, Code Analysis" category

### 4. MCP.so (chatmcp/mcpso) - ISSUE CREATED
- No PR-based submission: MCP.so is a curated Supabase-backed directory
- Created GitHub issue requesting listing: https://github.com/chatmcp/mcpso/issues/1445
- Status: Awaiting curator review

### 5. Official MCP Registry (modelcontextprotocol/registry) - BLOCKED
- Requires `mcp-publisher` CLI with GitHub device flow authentication
- Device flow requires interactive browser authorization at github.com/login/device
- Cannot be automated via CLI without browser interaction
- server.json is prepared and up-to-date at v1.19.0
- Action needed: Manual browser auth or set up GitHub Actions OIDC workflow

### 6. PulseMCP (pulsemcp.com) - BLOCKED
- Cloudflare blocks all curl/API requests from our VPS IP
- PulseMCP ingests from the official MCP Registry (daily, processed weekly)
- Once listed on official registry, PulseMCP listing would follow automatically
- Direct email option: team@pulsemcp.com

### 7. Smithery.ai - BLOCKED
- Not currently listed (confirmed via API: "Server not found")
- Requires Smithery API key from https://smithery.ai/account/api-keys
- CLI command: `npx @smithery/cli mcp publish --name "cosai-labs/toolpipe-mcp-server"`
- smithery.yaml is already prepared in the products/mcp-server directory
- Action needed: Create Smithery account and get API key

### 8. MCPServers.org - BLOCKED
- Form submission is client-side JavaScript (TanStack Router), no public API endpoint
- Requires browser-based form submission
- Fields: Server Name, Short Description, Link, Category (Development), Contact Email
- Free listings available, premium at $39 for faster review

### 9. MCPize.com - BLOCKED
- Requires `mcpize login` with email auth (interactive browser flow)
- `mcpize analyze` confirmed compatibility (95% confidence)
- Deploy command: `mcpize deploy` after auth
- Action needed: Create MCPize account and authenticate

## Summary

| Registry | Status | URL |
|---|---|---|
| Awesome MCP Servers | PR Open | https://github.com/punkpeye/awesome-mcp-servers/pull/3995 |
| Awesome MCP List | PR Open | https://github.com/MobinX/awesome-mcp-list/pull/166 |
| Glama.ai | Listed | https://glama.ai/mcp/servers/Aldric-Core/toolpipe-mcp-server |
| MCP.so | Issue Created | https://github.com/chatmcp/mcpso/issues/1445 |
| Official MCP Registry | Blocked (auth) | Needs interactive browser auth |
| PulseMCP | Blocked (Cloudflare) | Needs official registry first |
| Smithery.ai | Blocked (API key) | Needs account creation |
| MCPServers.org | Blocked (JS form) | Needs browser submission |
| MCPize.com | Blocked (auth) | Needs account creation |

## Next Steps
1. Use Playwright MCP or browser automation to complete Smithery, MCPServers.org, and MCPize submissions
2. Set up GitHub Actions workflow for mcp-publisher OIDC auth to publish to official registry
3. Monitor PR #3995 on awesome-mcp-servers for merge
