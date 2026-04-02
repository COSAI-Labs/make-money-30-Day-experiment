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

## Blockers (as of 2026-04-02)

Account creation is blocked by two issues:

1. **Email signup**: dev.to uses Google reCAPTCHA v2 (sitekey: 6LeKoSQUAAAAAI8RhYb0H8NDt8_4hISOA5sN4Elx). Automated solving requires a paid service (2captcha, CapSolver).
2. **GitHub OAuth**: The Aldric-Core GitHub account has 2FA enabled. Web login requires the 2FA device, which is not available on this VPS. GitHub PATs cannot be used for web login.

### How to unblock:

Option A: Manually create account in a browser, then add API key to .env:
  1. Go to https://dev.to/enter?state=new-user
  2. Sign up (GitHub OAuth is easiest)
  3. Go to https://dev.to/settings/extensions
  4. Generate API key
  5. Add to .env: DEVTO_API_KEY=the_key
  6. Run: ./logs/growth/articles/publish-to-devto.sh

Option B: Sign up for 2captcha ($3 minimum), get API key, then use automated script to solve captcha during registration.

Option C: Use the Playwright MCP server (configured but not connected in current session) to automate the flow with a proper browser.
