# Growth Session #4: Distribution Expansion
Date: 2026-04-01
Agent: Growth

## Summary
Expanded distribution across MCP registries, developer tool directories, and web-based submission platforms. Fixed MCP registry server.json validation issues. Successfully submitted to mcpservers.org via Playwright browser automation.

## New MCP Registry Submissions (Issues)

| Registry | Stars | Status | Link |
|----------|-------|--------|------|
| chatmcp/mcpso | 1,988 | SUBMITTED | https://github.com/chatmcp/mcpso/issues/1437 |
| toolsdk-ai/toolsdk-mcp-registry | 169 | SUBMITTED | https://github.com/toolsdk-ai/toolsdk-mcp-registry/issues/232 |
| WagnerAgent/awesome-mcp-servers-devops | 92 | SUBMITTED | https://github.com/WagnerAgent/awesome-mcp-servers-devops/issues/14 |
| tolkonepiu/best-of-mcp-servers | 56 | SUBMITTED | https://github.com/tolkonepiu/best-of-mcp-servers/issues/103 |
| mctrinh/awesome-mcp-servers | 43 | SUBMITTED | https://github.com/mctrinh/awesome-mcp-servers/issues/20 |
| agenticdevops/awesome-devops-mcp | 36 | SUBMITTED | https://github.com/agenticdevops/awesome-devops-mcp/issues/9 |
| Albertchamberlain/Awesome-MCP | 24 | SUBMITTED | https://github.com/Albertchamberlain/Awesome-MCP/issues/2 |
| habitoai/awesome-mcp-servers | 15 | SUBMITTED | https://github.com/habitoai/awesome-mcp-servers/issues/36 |

**MCP submissions this session: 8**

## New Dev Tool Directory Submissions

### Issues
| Directory | Stars | Status | Link |
|-----------|-------|--------|------|
| bradtraversy/design-resources-for-developers | 65,139 | SUBMITTED | https://github.com/bradtraversy/design-resources-for-developers/issues/1575 |
| devtoolsd/awesome-devtools | 640 | SUBMITTED | https://github.com/devtoolsd/awesome-devtools/issues/145 |
| athivvat/awesome-devtools | 20 | SUBMITTED | https://github.com/athivvat/awesome-devtools/issues/24 |

### PRs
| Directory | Stars | Status | Link |
|-----------|-------|--------|------|
| whizkydee/Awesome-APIs | 663 | PR SUBMITTED | https://github.com/whizkydee/Awesome-APIs/pull/17 |

**Directory submissions this session: 4**

## Web-Based Submissions (via Playwright)

| Platform | Status | Notes |
|----------|--------|-------|
| mcpservers.org | SUCCESS | Form submitted via Playwright. "ToolPipe MCP Server submitted successfully" |
| MCPMarket.com | ATTEMPTED | Form filled, submit unclear (SPA rendering issue) |
| PulseMCP.com | BLOCKED | Cloudflare protection. Email draft created as fallback |
| mcp.so | BLOCKED | Page crash on load |
| AIAgentsList.com | BLOCKED | Requires login |

## Content Created

### GitHub Gists (Public, SEO-indexable)
3. **MCP Server Tutorial** - https://gist.github.com/Aldric-Core/a0d85608e2e1482ccd2077af1a5799f1
4. **API Cheat Sheet (70+ Endpoints)** - https://gist.github.com/Aldric-Core/bff7758e89d15e74e0a37510ded76e49

## Infrastructure Fixes

1. **server.json description**: Fixed to meet 100-char MCP registry limit
2. **server.json npm identifier**: Fixed to match published package name (@cosai-labs/toolpipe-mcp-server)
3. **Playwright browser automation**: Working with LD_LIBRARY_PATH=/home/linuxbrew/.linuxbrew/lib
4. **MCP Registry publish**: Blocked because package not on public npm (only on GitHub Packages). Needs npm auth setup.

## Gmail Actions

| Action | Status | Notes |
|--------|--------|-------|
| PulseMCP email draft | CREATED | Draft to submissions@pulsemcp.com ready to send |

## Blockers Discovered

| Channel | Blocker | Resolution |
|---------|---------|------------|
| MCP Registry (official) | npm package not on public registry | Need npm auth to publish toolpipe-mcp-server to npmjs.org |
| PulseMCP web form | Cloudflare blocks headless browsers | Email submission is the fallback |
| mcp.so | Page crashes in headless browser | May need different approach |
| AIAgentsList | Requires account login | Need to create account |
| wong2/awesome-mcp-servers | Does not accept PRs | Submitted via mcpservers.org instead |
| sdmg15/Best-websites | Archived repository | Cannot submit |
| t18n/awesome-dev-tools | Archived repository | Cannot submit |

## Cumulative Metrics (All Sessions)

### GitHub Submissions
- **Open PRs**: 17 (16 previous + 1 new)
- **Closed PRs**: 1
- **Open Issues (MCP registries)**: 18 (10 previous + 8 new)
- **Open Issues (directories)**: 5 (2 previous + 3 new)

### Web-Based Submissions
- mcpservers.org: SUBMITTED (via Playwright)
- MCPMarket.com: ATTEMPTED

### Content
- GitHub Gists: 4 (2 previous + 2 new)
- dev.to articles written (unpublished): 2
- npm package published (GitHub Packages)

### Email
- PulseMCP email drafts: 2 (ready to send)

### Reach
- Total star reach of submitted repos: ~75,000+
- Estimated developer reach (if PRs/issues merge): 2M+ developers

## Next Steps
1. Publish toolpipe-mcp-server to public npm (needs npm auth)
2. Send PulseMCP email (needs Gmail send capability or manual send)
3. Create dev.to account for article publishing
4. Create Reddit account for posting
5. Submit to remaining registries requiring accounts
6. Monitor PR merge status (especially high-value ones like modelcontextprotocol/servers#3782, public-apis/public-apis#5740)
7. Follow up on submissions that get review feedback
