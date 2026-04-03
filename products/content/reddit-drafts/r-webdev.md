# Title: I built 220+ free developer APIs you can use from any project (no signup, no API key)

## Body:

Hey r/webdev,

I've been building a collection of developer utility APIs that I wanted to share. The idea was simple: every tool a dev might need, as a REST endpoint, with zero friction.

**What it is:** 220+ endpoints covering common dev tasks.

**What makes it different:** No signup. No API key needed. Just curl it.

Some examples:

```bash
# Format messy JSON
curl -X POST https://toolpipe.dev/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"json_string": "{\"a\":1,\"b\":[2,3]}"}'

# Generate a QR code (returns PNG)
curl "https://toolpipe.dev/qr/generate?data=https://reddit.com&size=300" -o qr.png

# Quick DNS lookup
curl "https://toolpipe.dev/api/dns/lookup?domain=reddit.com"

# SHA256 hash
curl -X POST https://toolpipe.dev/api/hash/sha256 \
  -H "Content-Type: application/json" -d '{"text": "hello"}'
```

**Full categories:**
- Text: JSON/XML/YAML format, Base64, URL encode, Markdown to HTML
- Crypto: Hash, UUID, JWT decode, random strings
- Network: DNS, WHOIS, IP geo, SSL check
- Web: Screenshots, scraping, meta tags
- PDF: Merge, split, compress, HTML to PDF
- Data: Fake users, addresses, lorem ipsum
- SEO: Page analyzer, keyword density

Interactive docs: https://toolpipe.dev/docs

It's also available as an MCP server for AI agents (Claude, etc.): `npx @cosai-labs/toolpipe-mcp-server`

Open to feedback on what tools to add next. What dev utilities do you wish existed as a simple API call?
