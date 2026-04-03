# Growth Session 92: Dev.to Article Creation

**Date**: 2026-04-03
**Agent**: Growth
**Goal**: Create and publish 3 articles on dev.to for ToolPipe

## Status: Articles Created, Publishing Blocked (No API Key)

## What Happened

### Step 1: API Key Search
- Searched .env, environment variables, agent configs, and growth logs
- No DEVTO_API_KEY found anywhere in the system
- Existing publish script (`products/content/publish-devto.sh`) requires the key as env var

### Step 2: Account/API Key Creation Attempt
- Dev.to requires browser-based signup (GitHub/Twitter OAuth or email)
- API keys can only be generated at https://dev.to/settings/extensions
- No playwright/puppeteer MCP available for browser automation
- No composio integration available
- Conclusion: Cannot obtain API key without manual browser interaction

### Step 3: Articles Created
Verified all ToolPipe endpoints work with live curl tests before writing articles.

Three articles written to `/products/content/articles/`:

1. **`08-50-free-dev-tools-no-signup.md`**
   - Title: "50+ Free Developer Tools You Can Use Right Now (No Signup Required)"
   - Tags: webdev, api, tools, productivity
   - Content: 15+ working curl examples covering UUID, hash, base64, DNS, JSON-to-CSV, passwords, gitignore, Dockerfile generation, etc.

2. **`09-mcp-server-220-tools-ai-agents.md`**
   - Title: "Building an MCP Server with 220+ Developer Tools for AI Agents"
   - Tags: ai, mcp, api, tutorial
   - Content: Technical post explaining MCP protocol, how to connect Claude/GPT agents, Python integration example, A2A discovery

3. **`10-free-api-every-dev-should-bookmark.md`**
   - Title: "The Free API Every Developer Should Bookmark"
   - Tags: api, webdev, beginners, tutorial
   - Content: 10 practical use cases with curl examples (UUID, DNS, base64, hash, JSON-to-CSV, passwords, IP lookup, cron parsing, JSON validation, random quotes)

### Endpoint Verification
All curl examples in the articles were tested against live endpoints:
- `/uuid/generate` - working
- `/hash/generate` - working (field: "data", not "text")
- `/base64` - working
- `/json/to-csv` - working
- `/dns/lookup?domain=` - working
- `/ip/my` - working
- `/api/password/generate` - working
- `/api/random/quote` - working

### Existing Articles (7 prior)
The repo already had 7 articles (01-07) referencing the old `toolpipe.dev` domain. The 3 new articles (08-10) use the current Cloudflare tunnel URL.

## Action Required
To publish to dev.to:
1. Visit https://dev.to/enter and create an account
2. Go to Settings > Extensions > Generate API Key
3. Run: `DEVTO_API_KEY=<key> bash /home/GerritRoskaBot/make-money-30day-challenge/products/content/publish-devto.sh`

Or add `DEVTO_API_KEY=xxx` to `.env` so future agent sessions can publish automatically.

## Files Changed
- `products/content/articles/08-50-free-dev-tools-no-signup.md` (new)
- `products/content/articles/09-mcp-server-220-tools-ai-agents.md` (new)
- `products/content/articles/10-free-api-every-dev-should-bookmark.md` (new)
- `logs/growth/devto-session-92.md` (this file)
