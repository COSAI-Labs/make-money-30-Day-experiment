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
- [ ] dev.to account created
- [ ] API key obtained
- [ ] Articles published
