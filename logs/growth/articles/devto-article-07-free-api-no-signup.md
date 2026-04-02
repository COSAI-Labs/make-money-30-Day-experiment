# 238+ Free APIs That Need Zero Signup

Tired of creating accounts just to test an API? Here are 238+ developer utility APIs you can use right now with just curl. No API key, no registration, no OAuth dance.

## Quick Examples

### Generate a QR Code

```bash
curl -X POST https://toolpipe.dev/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"data": "https://github.com"}' \
  --output qr.png
```

### Format JSON

```bash
curl -X POST https://toolpipe.dev/json/format \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"messy\":\"json\",\"no\":\"indentation\"}"}'
```

### DNS Lookup

```bash
curl "https://toolpipe.dev/dns/lookup?domain=github.com"
```

### Generate UUID

```bash
curl https://toolpipe.dev/uuid/generate
```

### Hash a String

```bash
curl -X POST https://toolpipe.dev/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "algorithm": "sha256"}'
```

## Full API Categories

### Text & Data Processing
- JSON formatting and validation
- JSON to CSV conversion
- Base64 encode/decode
- Markdown to HTML
- Text analysis (word count, readability, sentiment)
- ROT13 encoding
- URL encode/decode

### Code & DevOps
- Code review (AI-powered)
- Dockerfile generation
- .gitignore generation
- SQL formatting
- Regex testing
- JWT decoding
- Cron expression parsing

### Web & Network
- DNS lookup (A, AAAA, MX, NS, TXT)
- WHOIS queries
- SSL certificate checking
- URL metadata extraction (Open Graph)
- URL shortening
- HTTP header inspection
- Security header analysis

### Media & Visual
- QR code generation
- Image resizing
- Image format conversion
- PDF generation (HTML to PDF)
- Color conversion (HEX/RGB/HSL)
- CSS gradient generation
- Favicon extraction

### Utilities
- UUID generation (v4)
- Password generation
- Lorem ipsum generation
- Timestamp conversion
- IP geolocation
- User agent parsing
- Markdown table generation

## For AI Agents (MCP)

All 238+ tools are also available as an MCP server. Add to your Claude Code config:

```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://toolpipe.dev/mcp"
    }
  }
}
```

Listed on the [Official MCP Registry](https://registry.modelcontextprotocol.io) as `io.github.COSAI-Labs/toolpipe-mcp-server`.

## Source Code

Everything is open source: [GitHub Repository](https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/api-service)

---

*Tags: api, webdev, tools, productivity*
