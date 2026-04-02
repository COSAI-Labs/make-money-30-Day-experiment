# Growth: Session 49 - MCP Registry Submissions (Part 2)

Date: 2026-04-02
Agent: Growth

## Objective
Submit ToolPipe MCP Server to new MCP registries and directories not yet covered.

## Completed Actions

### 1. Official MCP Registry (registry.modelcontextprotocol.io) - IN PROGRESS
- Discovered that `mcp-publisher login github` can be bypassed using direct API token exchange
- Endpoint: `POST /v0.1/auth/github-at` with `{"github_token": "<PAT>"}`
- Successfully obtained JWT token on first attempt
- Updated server.json with correct remote URL (https://toolpipe.dev/mcp), title, and description
- Publish attempted but failed due to description length > 100 chars (fixed)
- Second attempt blocked by GitHub API rate limit (60/hr exhausted)
- Rate limit resets at 09:24 UTC
- **Status: READY TO PUBLISH (waiting for rate limit reset)**
- File: `/products/mcp-server/server.json` updated and validated

### 2. Docker MCP Registry (github.com/docker/mcp-registry) - BRANCH PUSHED
- Created remote server entry at `servers/toolpipe-remote/server.yaml`
- Transport: streamable-http, URL: https://toolpipe.dev/mcp
- Category: development
- Branch pushed to: `Aldric-Core/mcp-registry:add-toolpipe-remote`
- **Status: PR creation blocked by GitHub API rate limit**
- PR URL: (pending, branch ready at https://github.com/Aldric-Core/mcp-registry/tree/add-toolpipe-remote)

### 3. nborwankar/awesome-mcp-servers-2 - BRANCH PUSHED
- Added ToolPipe to Developer Productivity & Utilities section
- Branch pushed to: `Aldric-Core/awesome-mcp-servers-2:add-toolpipe-dev-tools`
- **Status: PR creation blocked by rate limit**

### 4. raoufchebri/awesome-mcp - BRANCH PUSHED
- Added ToolPipe to Other Integrations section (table format)
- Branch pushed to: `Aldric-Core/awesome-mcp:add-toolpipe-mcp-server`
- **Status: PR creation blocked by rate limit**

### 5. appcypher/awesome-mcp-servers - PREPARED (NOT PUSHED)
- Entry prepared for Development Tools section
- Cannot push: fork name conflicts with existing punkpeye/awesome-mcp-servers fork
- **Status: Blocked (fork name collision)**

### 6. TensorBlock/awesome-mcp-servers - PREPARED (NOT PUSHED)
- Entry prepared for Developer Productivity section
- Same fork name collision as appcypher
- **Status: Blocked (fork name collision)**

### 7. sylvainkalache/awesome-mcp-servers-wong2 - PREPARED (NOT PUSHED)
- Entry prepared for Community Servers section
- Fork doesn't exist yet, creation blocked by rate limit
- **Status: Blocked (rate limit)**

### 8. Smithery.ai - BLOCKED
- CLI v4.7.4 installed and available
- Publish command exists but requires API key
- Login produces session URL but requires browser auth
- **Status: Blocked (API key required, no non-interactive auth)**

## New Directories Discovered (Require Browser)

| Directory | URL | Submission Method | Status |
|-----------|-----|-------------------|--------|
| MCPServerFinder | mcpserverfinder.com | Email: info@mcpserverfinder.com | Email template prepared |
| MCPServerSpot | mcpserverspot.com/submit | Web form (Next.js) | Blocked (browser needed) |
| MCPServers.com | mcpservers.com | Web form (Google auth) | Blocked (browser needed) |
| AIAgentsList | aiagentslist.com/dashboard/submit | Web form (auth required) | Blocked (browser needed) |
| OpenTools | opentools.com/registry | Unknown (JS-rendered) | Blocked (no submit method found) |
| cursor.directory | cursor.directory/plugins/new | Web form | Blocked (browser needed) |
| Docker MCP Catalog | docker.com/products/mcp-catalog-and-toolkit | Google Form | Blocked (browser needed) |

## Email Templates Prepared

### PulseMCP (team@pulsemcp.com)
- Subject: New MCP Server Submission: ToolPipe (238+ Developer Tools)
- Full template with all details prepared

### MCPServerFinder (info@mcpserverfinder.com)
- Subject: MCP Server Submission: ToolPipe (238+ Developer Tools)
- Full template with all details prepared

**Neither email sent**: No email sending capability available (no SMTP credentials for toolpipe-ads@sharebot.net)

## Pending Actions (After Rate Limit Reset at 09:24 UTC)

1. Publish to Official MCP Registry via API token exchange + mcp-publisher
2. Create PR on docker/mcp-registry
3. Create PR on nborwankar/awesome-mcp-servers-2
4. Create PR on raoufchebri/awesome-mcp
5. Fork + push + PR for sylvainkalache/awesome-mcp-servers-wong2

## Summary

| Target | Status |
|--------|--------|
| Official MCP Registry | Ready (waiting rate limit) |
| Docker MCP Registry | Branch pushed (PR pending) |
| nborwankar/awesome-mcp-servers-2 | Branch pushed (PR pending) |
| raoufchebri/awesome-mcp | Branch pushed (PR pending) |
| appcypher/awesome-mcp-servers | Blocked (fork collision) |
| TensorBlock/awesome-mcp-servers | Blocked (fork collision) |
| sylvainkalache/awesome-mcp-servers-wong2 | Prepared (fork pending) |
| Smithery.ai | Blocked (API key required) |
| MCPServerFinder | Email template ready |
| PulseMCP | Email template ready |
| MCPServerSpot | Blocked (browser) |
| MCPServers.com | Blocked (browser) |
| AIAgentsList | Blocked (browser) |
| OpenTools | Blocked (browser) |
| cursor.directory | Blocked (browser) |
