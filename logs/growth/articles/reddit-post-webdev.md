# Reddit Post: r/webdev

**Title:** I built 230+ free developer utility APIs with no signup required

**Body:**

Hey r/webdev,

I built a collection of 230+ developer utility APIs that are completely free and require no signup, no API key, and no auth headers. Just HTTP requests.

Some highlights:

- **JSON formatter/validator** - Format, validate, minify
- **QR code generator** - POST data, get PNG back
- **Hash generator** - MD5, SHA256, SHA512
- **UUID generator** - v4 UUIDs
- **DNS lookup** - A, MX, NS, TXT records
- **Base64 encode/decode**
- **Markdown to HTML**
- **JWT decoder**
- **WHOIS lookup**
- **Web scraper** - Extract content from any URL
- **PDF tools** - Merge, split, compress, extract text
- **Code review** - AI-powered code analysis
- **Fake data generator** - Names, emails, addresses for testing
- **SEO analyzer** - Analyze any URL for SEO issues
- **Screenshot API** - Capture any webpage
- And 200+ more

Everything is CORS-enabled so you can call it from browser JS. There's also an MCP server if you want to give these tools to your AI coding agent (Claude, Cursor, etc.).

Quick example:

```bash
# Generate a QR code
curl -X POST https://toolpipe.dev/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"data": "https://example.com"}' --output qr.png

# Look up DNS records
curl "https://toolpipe.dev/dns/lookup?domain=example.com"

# Generate a UUID
curl https://toolpipe.dev/uuid/generate
```

Website: https://toolpipe.dev
API Docs: https://toolpipe.dev/docs
MCP Server: `npx -y @cosai-labs/toolpipe-mcp-server`

Would love feedback on what other tools would be useful. What developer utilities do you find yourself googling for regularly?
