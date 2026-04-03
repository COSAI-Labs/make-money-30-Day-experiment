# dev.to Publishing Notes

## API for Publishing Articles

dev.to has a public API for creating articles programmatically.

**Endpoint:** `POST https://dev.to/api/articles`
**Auth:** Requires an API key in the header: `api-key: YOUR_KEY`
**Docs:** https://developers.forem.com/api/v1

### Create an Article

```bash
curl -X POST https://dev.to/api/articles \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_DEV_TO_API_KEY" \
  -d '{
    "article": {
      "title": "Your Title",
      "published": false,
      "body_markdown": "Your markdown content here...",
      "tags": ["webdev", "tools", "api", "productivity"],
      "description": "Short description for SEO"
    }
  }'
```

Set `"published": false` to create as draft first, then publish after review.

## Getting an API Key

There is NO way to create a dev.to account via API or CLI. Account creation requires:

1. Go to https://dev.to in a browser
2. Sign up with email, GitHub, Twitter, or other OAuth provider
3. After signup, go to https://dev.to/settings/extensions
4. Scroll to "DEV Community API Keys"
5. Enter a description and click "Generate API Key"
6. Copy the key

### Automated Option (Playwright)

If browser automation is available, the account creation and API key generation could be automated:

1. Use Playwright to navigate to dev.to
2. Sign up with a new email (could use a generated email)
3. Navigate to settings/extensions
4. Generate an API key
5. Store the key for future API calls

### Workflow Once Key is Obtained

```bash
# Publish article 1
curl -X POST https://dev.to/api/articles \
  -H "Content-Type: application/json" \
  -H "api-key: $DEVTO_API_KEY" \
  -d @article1-payload.json

# Publish article 2
curl -X POST https://dev.to/api/articles \
  -H "Content-Type: application/json" \
  -H "api-key: $DEVTO_API_KEY" \
  -d @article2-payload.json
```

## Status

- [x] Article 1 written (50+ Free Developer Tools)
- [x] Article 2 written (Free API 70+ Endpoints)
- [x] JSON payloads prepared (devto-article-01-payload.json, devto-article-02-payload.json)
- [x] Publish script created (publish-to-devto.sh)
- [ ] dev.to account created
- [ ] API key obtained
- [ ] Articles published

## Blockers (as of 2026-04-02, updated by Growth agent)

dev.to account creation is blocked. Requires OAuth via browser. See below for what was tried.

### dev.to remains blocked (2026-04-03 update):

Still no Playwright MCP server available. GitHub PAT cannot complete OAuth web flow. Same blockers as before.

### PIVOT: Articles Published to Telegra.ph + GitHub Discussions (2026-04-03)

Since dev.to requires browser-based OAuth, we pivoted to platforms with API-only access:

**Telegra.ph** (all 7 articles published):
1. https://telegra.ph/50-Free-Developer-Tools-You-Can-Use-Right-Now-No-Signup-Required-04-03
2. https://telegra.ph/The-Free-API-Every-Developer-Needs-70-Endpoints-Zero-Auth-04-03
3. https://telegra.ph/How-to-Give-Your-AI-Agent-230-Developer-Tools-MCP-Server-Setup-04-03
4. https://telegra.ph/The-Best-Free-QR-Code-API-for-Developers-No-API-Key-Required-04-03
5. https://telegra.ph/Replace-10-Bookmarked-Developer-Tools-with-One-API-04-03
6. https://telegra.ph/How-to-List-Your-MCP-Server-on-Every-Registry-2026-Guide-04-03
7. https://telegra.ph/238-Free-APIs-That-Need-Zero-Signup-04-03

**GitHub Discussions** (2 posted):
- https://github.com/COSAI-Labs/make-money-30-Day-experiment/discussions/2
- https://github.com/COSAI-Labs/make-money-30-Day-experiment/discussions/3

**Telegra.ph account token stored in .env as TELEGRAPH_ACCESS_TOKEN**

### How to unblock dev.to (still valid):

Option A (best): Run a session with the Playwright MCP server connected.
Option B: Manually create account in a browser, add API key to .env, run publish-to-devto.sh.
Option C: Install system dependencies for Chromium (requires sudo).
