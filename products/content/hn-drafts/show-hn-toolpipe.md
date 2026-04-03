# Show HN: ToolPipe - 220+ Free Developer APIs (No Signup Required)

I built ToolPipe, a collection of 220+ developer utility APIs that you can use right now without signing up for anything.

**Live API**: https://toolpipe.dev
**Docs**: https://toolpipe.dev/docs
**GitHub**: https://github.com/COSAI-Labs/toolpipe

## What it does

Every tool is a simple REST endpoint. No API keys needed for the free tier (100 calls/day).

Quick examples:

```bash
# Format JSON
curl -X POST https://toolpipe.dev/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"json_string": "{\"name\":\"test\",\"value\":42}"}'

# Generate QR code
curl "https://toolpipe.dev/qr/generate?data=hello&size=200"

# Hash a string
curl -X POST https://toolpipe.dev/api/hash/sha256 \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world"}'

# Generate UUID
curl https://toolpipe.dev/api/uuid/generate

# DNS lookup
curl "https://toolpipe.dev/api/dns/lookup?domain=example.com"
```

## Tools include

- **Text**: JSON/XML/YAML format, Base64, URL encode/decode, Markdown to HTML
- **Crypto**: Hash (MD5, SHA256, bcrypt), UUID, random string, JWT decode
- **Network**: DNS lookup, WHOIS, IP geolocation, HTTP headers, SSL check
- **Web**: Screenshot, scrape, meta tags, robots.txt, sitemap parse
- **SEO**: Analyzer, keyword density, backlink check, page speed
- **PDF**: Merge, split, compress, rotate, watermark, HTML to PDF
- **Data**: Fake users, addresses, companies, credit cards, lorem ipsum
- **Dev**: Regex tester, cron parser, code review, diff tool

## Also available as MCP server

AI agents can use all these tools via MCP protocol:

```bash
npx @cosai-labs/toolpipe-mcp-server
```

## Tech stack

Built with FastAPI (Python), running on a VPS with Cloudflare tunnel. The whole thing started as an experiment in how much useful tooling you can ship in a weekend.

Happy to answer any questions about the architecture or add tools you'd find useful.
