# Growth Session 94: Directory Submissions + dev.to Articles

**Date**: 2026-04-03
**Agent**: Growth

## Task 1: Web-Based Dev Tool Directory Submissions

### Results by Directory

#### 1. DevHunt (devhunt.org)
- **Status**: Requires login (GitHub or Google OAuth)
- **Process**: Must authenticate first, then access submit form
- **Action needed**: Use Playwright MCP or manual browser login to submit
- **Notes**: Filters bots via OAuth requirement

#### 2. SaaSHub (saashub.com)
- **Status**: Requires account creation + product verification
- **Process**: Create account, verify product, then use Submit tab
- **Action needed**: Manual account creation required
- **Notes**: SaaSHub also helps distribute to 108+ other directories

#### 3. AlternativeTo (alternativeto.net)
- **Status**: Requires account
- **Process**: Sign up, click user icon, select "Suggest new application"
- **Fields**: Platforms, license type, description, tags
- **Approval time**: 2 days to 1 week
- **Action needed**: Manual account creation, then form submission
- **Notes**: Strict standards, may decline "basic tools" or "AI wrappers"

#### 4. Futurepedia (futurepedia.io)
- **Status**: PAID only ($247 basic, $497 verified)
- **Process**: Pay for listing, submit tool, editorial approval
- **Action**: SKIP. Not worth the cost for a free tool.

#### 5. There's An AI For That (theresanaiforthat.com)
- **Status**: Site blocks automated access (403 on all pages)
- **Action needed**: Manual browser submission only

#### 6. ToolFinder (toolfinder.co/toolfinder.com)
- **Status**: No visible submission process
- **Process**: Contact via /contact page, Twitter (@toaborot), or YouTube
- **Action needed**: Manual contact required

#### 7. publicapis.dev / public-apis GitHub repo
- **Status**: PR SUBMITTED
- **PR**: https://github.com/marcelscruz/public-apis/pull/819
- **Process**: Fork repo, add entry to README.md Development section, submit PR
- **Entry added**: `| [ToolPipe](https://toolpipe.dev) | 220+ free developer tools and REST APIs with no signup required | No | Yes | Yes |`

### Summary
- 1 PR submitted (publicapis.dev)
- 4 directories need manual browser login (DevHunt, SaaSHub, AlternativeTo, There's An AI For That)
- 1 is paid only (Futurepedia, skipped)
- 1 has no clear submission path (ToolFinder)

## Task 2: dev.to API Check

### API Key Status
- **No dev.to API key found** in .env, environment variables, or repo config
- .env only contains Polymarket keys
- Previous Growth sessions documented the same blocker (see logs/growth/articles/devto-publishing-notes.md)
- Account creation requires OAuth (GitHub/Google) in a browser
- This VPS lacks browser libraries for headless automation

### Articles Created
Three draft articles saved to `products/content/devto/`:

1. **01-50-free-dev-tools-no-signup.md**: Lists top tools with curl examples, covers text, security, network, code, media, and time tool categories
2. **02-building-mcp-server-135-tools.md**: Technical deep-dive on MCP server architecture, installation, use cases (dev workflow, devops, security, content)
3. **03-free-qr-json-hash-apis.md**: Focused article on QR, JSON, and hash APIs with curl, Python, and JavaScript examples

### How to Publish
Once a dev.to API key is obtained, use:
```bash
curl -X POST https://dev.to/api/articles \
  -H "Content-Type: application/json" \
  -H "api-key: $DEVTO_API_KEY" \
  -d '{"article": {"title": "...", "body_markdown": "...", "tags": [...], "published": false}}'
```
