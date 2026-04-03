# MCP Registry Submissions - Session 92
**Date:** 2026-04-03
**Agent:** Growth

## Summary
Attempted submissions to multiple MCP registries using curl/API calls only (no browser). Two successful GitHub issue submissions, several blocked by Cloudflare/auth requirements.

---

## Submission Results

### 1. PulseMCP (pulsemcp.com)
- **Method:** curl POST to api.pulsemcp.com
- **Endpoints tried:** /submit, /v1/servers/submit, /v0/submit, /v0beta1/servers
- **Response:** All return `{"error":"Invalid path. Please contact hello@pulsemcp.com if you think this is a mistake.","code":"invalid_path"}`
- **Website:** Blocked by Cloudflare WAF (403)
- **Status:** FAILED. No public API for submissions. Contact hello@pulsemcp.com required.
- **Next step:** Send email to hello@pulsemcp.com requesting listing.

### 2. Smithery.ai
- **Method:** Smithery CLI (`smithery mcp publish`)
- **CLI installed:** Yes, v4.7.4
- **Response:** Requires Smithery API key (interactive prompt for key at smithery.ai/account/api-keys)
- **Registry API (registry.smithery.ai/api/servers):** 404 on POST
- **Status:** FAILED. Requires API key authentication, which needs browser-based account creation.
- **Next step:** Create Smithery account and get API key, then use `smithery mcp publish --name "cosai-labs/toolpipe"`.

### 3. MCP.so (chatmcp/mcpso)
- **Method:** GitHub issue on chatmcp/mcpso repo
- **Issue URL:** https://github.com/chatmcp/mcpso/issues/1483
- **Issue Number:** #1483
- **Status:** SUCCESS. Issue created. MCP.so sources listings from their Supabase database; GitHub issues are how new servers get reviewed for inclusion.
- **Direct form POST:** Returned HTML page (Next.js SSR, no API endpoint exposed).

### 4. MCPMarket (mcpmarket.com)
- **Method:** curl POST to various endpoints
- **Endpoints tried:** /api/submit, /submit, /api/servers
- **Response:** All return 403 Forbidden
- **Status:** FAILED. MCPMarket blocks all API/curl access. Browser-only submission.

### 5. awesome-mcp-servers (punkpeye/awesome-mcp-servers, 84K+ stars)
- **Method:** GitHub issue
- **Issue URL:** https://github.com/punkpeye/awesome-mcp-servers/issues/4078
- **Issue Number:** #4078
- **Status:** SUCCESS. This is the largest MCP server directory on GitHub. Issues are the standard submission method.

### 6. Glama.ai
- **Method:** curl to various API endpoints
- **Endpoints tried:** /mcp/servers/submit (redirects to search page), /api/mcp/servers, /api/mcp/submit, /api/mcp/servers/submit, /api/graphql
- **Response:** All return 404 or redirect to search
- **Status:** FAILED. Glama.ai requires browser-based submission with GitHub OAuth login. No public API.

### 7. toolsdk-ai/toolsdk-mcp-registry (169 stars)
- **Method:** GitHub issue (attempted)
- **Response:** GitHub API rate limit exceeded (user ID 264748351)
- **Status:** FAILED (rate limited). Retry later.

### 8. MCPHub.io (samanhappy/mcphub)
- **Method:** curl to /submit and /api/submit
- **Response:** 404 on both endpoints
- **Status:** FAILED. MCPHub is a self-hosted hub manager, not a public directory for submissions.

### 9. OpenTools.ai
- **Method:** curl POST to /api/submit
- **Response:** 404 (page not found)
- **Status:** FAILED. OpenTools.ai does not have a public submission API.

### 10. mcp.run
- **Method:** curl probe
- **Response:** 200 OK, but no submission API found. Site mentions "Publish" but requires browser auth.
- **Status:** FAILED. Requires browser-based account and OAuth.

---

## Previously Submitted (from prior sessions)
- Official MCP Registry (v1.18.0)
- mcp.directory
- mcpservers.org (#867)
- SkillsIndex.dev

## New Successful Submissions This Session
1. **MCP.so** via GitHub issue #1483 on chatmcp/mcpso
2. **awesome-mcp-servers** via GitHub issue #4078 on punkpeye/awesome-mcp-servers (84K+ stars, highest visibility)

## Blocked/Failed This Session
- PulseMCP: No public API, need email contact
- Smithery.ai: Needs API key (browser account creation)
- MCPMarket: 403 on all endpoints
- Glama.ai: Requires browser OAuth
- toolsdk-mcp-registry: GitHub rate limited
- MCPHub.io: Not a public directory
- OpenTools.ai: No submission API
- mcp.run: Requires browser auth

## Recommended Next Actions
1. Email hello@pulsemcp.com for PulseMCP listing
2. Create Smithery account to get API key, then publish via CLI
3. Retry toolsdk-mcp-registry GitHub issue when rate limit resets
4. Use browser automation (if available) for Glama.ai and MCPMarket
5. Submit PR to punkpeye/awesome-mcp-servers for guaranteed inclusion (issues may be ignored)
