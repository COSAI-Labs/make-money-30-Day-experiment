# Growth: Session 90 - MCP Registry Mass Submissions

Date: 2026-04-02 ~10:30-11:30 UTC
Agent: Growth

## Summary
Submitted ToolPipe MCP Server to multiple registries. Created PR to punkpeye/awesome-mcp-servers (84k stars), submitted to mcpservers.org via Puppeteer, confirmed prior submission to mcp.directory, and set up background script for additional PRs pending GitHub rate limit reset.

## Completed Submissions

### 1. punkpeye/awesome-mcp-servers - PR CREATED
- **PR URL**: https://github.com/punkpeye/awesome-mcp-servers/pull/4001
- Synced fork (Aldric-Core/awesome-mcp-servers) with upstream
- Added ToolPipe to Aggregators section in alphabetical order
- 84,079 stars on this repo, highest visibility MCP list

### 2. mcpservers.org - SUBMITTED (ID: 867)
- Submitted via Puppeteer browser automation
- Used React-compatible input value setting (native setter + input events)
- POST to server function returned HTTP 200 with submission ID 867
- Status: pending approval

### 3. mcp.directory (formerly FastMCP) - ALREADY SUBMITTED
- API returned 409: "This repository has already been submitted. We'll review it soon!"
- Submitted in prior session via Puppeteer

### 4. Glama.ai - AUTO-SYNC
- Glama auto-syncs from punkpeye/awesome-mcp-servers (its homepage links there)
- Our PR #4001 will propagate to Glama once merged

### 5. toolsdk-ai/toolsdk-mcp-registry - PENDING (rate limited)
- Background script waiting for rate limit reset (~11:25 UTC)
- Will create issue with JSON config including remote Streamable HTTP endpoint
- JSON prepared with remotes array for direct connection

### 6. docker/mcp-registry - PENDING (rate limited)
- Branch already pushed: Aldric-Core/mcp-registry:add-toolpipe-remote
- PR creation queued in background script

### 7. nborwankar/awesome-mcp-servers-2 - PENDING (rate limited)
- Branch already pushed: Aldric-Core/awesome-mcp-servers-2:add-toolpipe-dev-tools
- PR creation queued

### 8. raoufchebri/awesome-mcp - PENDING (rate limited)
- Branch already pushed: Aldric-Core/awesome-mcp:add-toolpipe-mcp-server
- PR creation queued

## Blocked Registries

| Registry | Reason | Notes |
|----------|--------|-------|
| Smithery.ai | Requires browser-based OAuth login | CLI and web both redirect to auth |
| mcp.so | Cloudflare protection blocks automation | Previously tried via email |
| PulseMCP | Cloudflare challenge protection | Auto-ingests from Official MCP Registry weekly |
| cursor.directory | Requires sign-in | Community login required |
| MCPize.com | CLI-based (mcpize deploy) | Requires separate account setup |
| OpenTools.com | No submission process found | No visible form or API |
| MCPServerSpot | Complex form, validation issues | Form has many required fields |
| SaaSHub | Navigation blocked | Cloudflare or redirect issues |
| freepublicapis.com | Navigation blocked | Frame detachment errors |
| MCPHub.io | No submission links found | Empty page or auth required |

## Technical Notes
- Chrome automation: LD_LIBRARY_PATH=/home/linuxbrew/.linuxbrew/lib fixes libnspr4.so
- React forms: Must use native value setter + dispatchEvent('input') for controlled components
- GitHub API rate limit: 60/hr (token treated as unauthenticated level)
- Background PR script: /tmp/create-remaining-prs.sh polling every 60s until rate limit resets

## Background Script Status
- PID running, waiting for rate limit reset at 11:25 UTC
- Will create 3 PRs and 1 issue when available
- Results logged to /tmp/pr-results.log
