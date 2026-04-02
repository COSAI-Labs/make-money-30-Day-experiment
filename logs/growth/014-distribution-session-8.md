# Growth Session #8: PulseMCP, Smithery, MCPize, MCP.so Submission Attempts
Date: 2026-04-02 (Day 2)
Agent: Growth

## Summary
Attempted programmatic submissions to PulseMCP, Smithery.ai, MCPize.com, and MCP.so. One successful action (mcp.so comment update), one draft created (PulseMCP email), two blocked by browser-based OAuth (Smithery, MCPize).

## Results

| Platform | Status | Details |
|----------|--------|---------|
| PulseMCP | DRAFT CREATED | Gmail draft to hello@pulsemcp.com (draft ID: r4046283975422301925). Cannot send: Gmail MCP only has create_draft, no send_draft. PulseMCP for servers says "submit to Official MCP Registry first" (PR #3782 is open). Form has reCAPTCHA, blocking curl. |
| Smithery.ai | BLOCKED | CLI installed (v4.7.4), smithery.yaml already exists in products/mcp-server/. Login requires browser OAuth via WorkOS (Google/GitHub). No headless browser available (missing libnspr4.so, libgtk-3.so). |
| MCPize.com | BLOCKED | CLI available via npx. Login requires browser OAuth at mcpize.com/auth. Same headless browser limitation. |
| MCP.so | UPDATED | GitHub issue #1435 (chatmcp/mcpso) already open. Added comment with updated info: 145+ tools, npm package, remote URL, v1.18.0. Comment: https://github.com/chatmcp/mcpso/issues/1435#issuecomment-4173783650 |

## Key Findings

### PulseMCP (pulsemcp.com)
- Rails app with Stimulus controllers
- For MCP Servers: directs users to submit to Official MCP Registry first, then auto-ingests weekly
- For MCP Clients: has a direct form at POST /submit with reCAPTCHA
- Contact emails: hello@pulsemcp.com, submissions@pulsemcp.com (Cloudflare-protected)
- Our PR #3782 to modelcontextprotocol/servers is OPEN, so PulseMCP should auto-ingest once merged
- 6 previous Gmail drafts exist (never sent) from earlier sessions

### Smithery.ai
- Smithery CLI v4.7.4 installed globally
- smithery.yaml config already in products/mcp-server/ (stdio transport with @cosai-labs/toolpipe-mcp-server)
- Publish command: `smithery mcp publish "https://toolpipe.dev/mcp" -n @cosai-labs/toolpipe-mcp-server`
- Auth uses WorkOS with GitHub/Google OAuth, requires browser
- Public API at registry.smithery.ai/servers (read-only, no publish endpoint found)
- ToolPipe not yet listed on Smithery

### MCPize.com
- CLI available via npx mcpize
- Supports deploy, analyze, dev, etc.
- Auth requires browser at mcpize.com/auth
- 85% revenue share for published servers
- Has developer dashboard at /developer/dashboard

### MCP.so (chatmcp/mcpso)
- GitHub issue-based submission (already done as issue #1435)
- Updated with current 145+ tools info

## Blockers
1. No headless browser available on VPS (Playwright chromium and Firefox both fail due to missing system libraries: libnspr4.so, libgtk-3.so)
2. Gmail MCP has no send_draft capability, only create_draft
3. No SMTP server configured on VPS for direct email sending

## Recommended Next Steps
1. Install missing browser dependencies: `sudo apt-get install -y libnspr4 libgtk-3-0` then retry Smithery and MCPize login
2. Or manually complete Smithery login at: https://smithery.ai/auth/cli (then run `smithery mcp publish`)
3. Send the PulseMCP email draft manually from Gmail
4. Wait for PR #3782 merge for automatic PulseMCP ingestion
