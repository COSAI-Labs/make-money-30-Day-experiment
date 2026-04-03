# Reddit Post: r/programming

**Title:** 220+ free developer utility APIs: JSON, regex, QR, PDF, DNS, hash, UUID, and more (no signup)

**Body:**

I packaged 220+ common developer utilities into a single API service. All free, no API key, no signup.

The idea: instead of bookmarking 20 different sites for JSON formatting, Base64 encoding, UUID generation, etc., hit one API.

Some examples:

```bash
# Format JSON
curl -s toolpipe.dev/json-formatter -d '{"messy":"json"}'

# Generate QR code
curl -s "toolpipe.dev/qr-code?data=https://example.com" > qr.png

# SHA-256 hash
curl -s "toolpipe.dev/hash-generator?text=hello&algorithm=sha256"

# DNS lookup
curl -s "toolpipe.dev/dns-lookup?domain=example.com"

# Regex test
curl -s "toolpipe.dev/regex-tester?pattern=\d+&text=abc123"
```

Full list: https://toolpipe.dev
API docs: https://toolpipe.dev/docs

Built with Python/FastAPI. Also available as an MCP server for AI coding agents.

What utilities do you reach for most often?
