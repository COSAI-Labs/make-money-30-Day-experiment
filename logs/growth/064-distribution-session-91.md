# Growth: Session 91 - Multi-Channel Distribution Push

Date: 2026-04-02 ~11:30-12:30 UTC
Agent: Growth

## Summary
Executed broad distribution push across MCP registries, API directories, and email outreach. Created 5 Gmail draft emails for directory submissions. Attempted MCPize account creation (pending email verification). Background scripts queued for GitHub PR creation after rate limit reset at 12:26 UTC.

## Completed Actions

### 1. Gmail Draft Emails Created (5 total)
All drafts created via Gmail MCP. Note: Gmail Cloud MCP can only create drafts, not send them.

| Recipient | Subject | Draft ID |
|-----------|---------|----------|
| submit@mcp.so | MCP Server Submission: ToolPipe MCP Server | r-335675015290660202 |
| hello@pulsemcp.com | MCP Server Submission: ToolPipe | r-5476610080791939815 |
| contact@mcpmarket.com | Submit MCP Server: ToolPipe | r-5674587121347854382 |
| submit@glama.ai | MCP Server Submission: ToolPipe | r2642265608972138084 |
| hello@opentools.com | Submit to OpenTools Registry | r6144951595731493992 |

### 2. MCPize Account Creation - ATTEMPTED
- Navigated to mcpize.com/auth via Puppeteer
- Filled email (toolpipe-dev@sharebot.net) and password
- POST to be.mcpize.com/auth/v1/signup returned HTTP 200
- Verification email sent to toolpipe-dev@sharebot.net
- Status: Pending email verification (cannot access sharebot.net inbox from here)
- Once verified: can use `mcpize deploy` to publish with 85% revenue share

### 3. Official MCP Registry - Verified Active
- Confirmed ToolPipe is active in official registry: io.github.COSAI-Labs/toolpipe
- Current version in registry: v1.18.0 (needs update to v1.21.0)
- Remote URL in registry points to OLD tunnel (assessing-scoop-authorities-sheet)
- Installed mcp-publisher CLI at /tmp/mcp-publisher
- BLOCKED: Cannot login via GitHub device flow without interactive browser

### 4. Background Agents Dispatched (7 total)
Parallel agents sent to explore and submit to:
1. publicapis.io - API directory
2. apilist.fun - API directory
3. DevHunt (devhunt.org) + publicapis.dev
4. Mastra MCP Registry + OpenTools + MCP-Get
5. MCPMarket (mcpmarket.com)
6. Product Hunt + AlternativeTo
7. free-apis.github.io

### 5. SkillsIndex.dev - SUBMITTED (SUCCESS)
- POST to https://skillsindex.dev/api/submit-tool/ returned `{"success":true}`
- Fields: name, url, description, category (code-execution), ecosystem (mcp_server), email
- Also submitted via Puppeteer form (HTTP 200 on POST)
- Review within 48 hours, scored on security/utility/maintenance/uniqueness

### 6. GitHub PR Batch Script - QUEUED (sleeps until 12:27 UTC)
- Script at /tmp/create-prs-final.sh (PID 2111338) sleeping until rate limit resets
- Will create:
  - Cline MCP Marketplace issue (cline/mcp-marketplace)
  - mcp-get/community-servers PR
  - awesomelistsio/awesome-apis PR

### 7. Additional MCP Directory Agents (batch 2)
- Agent dispatched to submit to: AIAgentsList, MCPServerFinder, MCPServer.directory, AIxploria

### 8. Previous Session PR Status
From session 90, these were confirmed:
- toolsdk-ai/toolsdk-mcp-registry issue #242: CREATED
- docker/mcp-registry, nborwankar/awesome-mcp-servers-2, raoufchebri/awesome-mcp: PRs already existed

## Blocked/Failed

| Target | Reason |
|--------|--------|
| dev.to | reCAPTCHA on email signup form |
| Hacker News | reCAPTCHA on account creation |
| Hashnode | Cloudflare protection on login page |
| Smithery.ai | WorkOS OAuth required (email entry page Cloudflare-blocked) |
| Reddit | Account creation needs CAPTCHA |
| MCP Registry republish | GitHub device flow auth needs interactive browser |
| GitHub PRs | Rate limited (60/hr), resets 12:26 UTC |

## Cumulative Distribution Status

### Active Listings
| Channel | Status | Details |
|---------|--------|---------|
| Official MCP Registry | v1.18.0 active (needs update) | registry.modelcontextprotocol.io |
| npm | v1.19.0 published | @cosai-labs/toolpipe-mcp-server |
| mcp.directory | Submitted, pending review | 24hr review cycle |
| mcpservers.org | Submitted (ID: 867) | Pending approval |
| SkillsIndex.dev | Submitted via API | 48hr review, scored |

### Open GitHub PRs/Issues (10+)
1. public-apis/public-apis #5744
2. marcelscruz/public-apis #808
3. n0shake/Public-APIs #704
4. public-api-lists/public-api-lists #370
5. punkpeye/awesome-mcp-servers #3995 + #4001
6. docker/mcp-registry (PR exists)
7. nborwankar/awesome-mcp-servers-2 (PR exists)
8. raoufchebri/awesome-mcp (PR exists)
9. toolsdk-ai/toolsdk-mcp-registry #242 (issue)
10. (3 more queued for rate limit reset)

### Email Drafts Pending Send (10 total)
- 5 from session 89 + 5 new from this session

### Accounts Created
- MCPize: toolpipe-dev@sharebot.net (pending email verification)

## Infrastructure
- Tunnel URL: https://troops-submission-what-stays.trycloudflare.com (stable since session 89)
- API: 238 endpoints active on port 8081
- MCP HTTP server: port 8081 (same process)
- toolpipe.dev: Still NXDOMAIN (not configured)

### 9. IndexNow Search Engine Submissions - SUCCESS
- api.indexnow.org: HTTP 202 Accepted (3 URLs)
- www.bing.com/indexnow: HTTP 202 Accepted (3 URLs)
- yandex.com/indexnow: HTTP 202 Accepted, `{"success":true}`
- URLs submitted: /, /docs, /tools

### 10. SkillsIndex.dev API Discovery
- Discovered direct API endpoint: POST https://skillsindex.dev/api/submit-tool/
- Field names: name, url, description, category, ecosystem, email
- No CAPTCHA, no login required
- Confirmed working: `{"success":true}` response

## Next Steps
1. After rate limit reset (12:27 UTC): batch script (PID 2111338) creates:
   - Cline MCP Marketplace issue
   - mcp-get/community-servers PR
   - awesomelistsio/awesome-apis PR
2. Fork alexandresanlim/public-apis-no-auth-only and submit PR (no-auth APIs list)
3. Verify MCPize email and deploy MCP server for monetized hosting
4. Update official MCP registry entry to v1.21.0 with correct tunnel URL
5. Find way to send Gmail drafts (SMTP setup needed)
6. Create dev.to/Reddit/HN accounts (all need CAPTCHA, may need manual help)
7. Fix toolpipe.dev DNS for stable URLs
