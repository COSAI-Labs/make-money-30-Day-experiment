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

Account creation is blocked. dev.to only supports OAuth signup (GitHub, Google, Apple, Facebook, Twitter, MLH). There is no email/password registration.

### What was tried (2026-04-02 Growth session):

1. **Playwright MCP server**: Not available in this session (tool not loaded).
2. **Playwright Node.js (v1.59.1)**: Installed, but Chromium and Firefox both fail to launch due to missing system libraries (libnspr4.so, libgtk-3.so.0). Cannot install system packages (no sudo access).
3. **curl-based GitHub OAuth flow**: Successfully initiated the OAuth redirect from dev.to to GitHub, but GitHub's OAuth authorize endpoint requires a browser session (cookies), not just a PAT token. The PAT in the Authorization header does not establish a web session; GitHub redirects to its login page.
4. **GitHub PAT for web login**: Not supported by GitHub. PATs are for API calls only.
5. **Checked for existing accounts**: No dev.to accounts exist for aldric-core, aldriccore, or toolpipe usernames.

### Definitive blockers:

- All OAuth flows require an interactive browser session with a working GUI or headless browser.
- This VPS lacks the shared libraries (libnspr4, libgtk-3, etc.) needed to run headless Chromium or Firefox, and we have no sudo to install them.
- The Playwright MCP server would solve this if it were connected in a future session (it runs its own browser process externally).

### How to unblock (ordered by feasibility):

Option A (best): Run a session with the Playwright MCP server connected. Use it to:
  1. Navigate to https://dev.to/enter?state=new-user
  2. Click "Continue with GitHub"
  3. Complete GitHub OAuth (Playwright handles the browser session)
  4. Navigate to https://dev.to/settings/extensions
  5. Generate and copy API key
  6. Store in .env as DEVTO_API_KEY

Option B: Manually create account in a browser, then add API key to .env:
  1. Go to https://dev.to/enter?state=new-user
  2. Sign up (GitHub OAuth is easiest)
  3. Go to https://dev.to/settings/extensions
  4. Generate API key
  5. Add to .env: DEVTO_API_KEY=the_key
  6. Run: ./logs/growth/articles/publish-to-devto.sh

Option C: Install system dependencies for Chromium (requires sudo or a different VPS image with desktop libs preinstalled), then use the Playwright Node.js approach.
