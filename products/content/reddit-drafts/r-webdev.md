# Reddit Post: r/webdev

**Subreddit:** r/webdev
**Type:** Text post
**Flair:** Showoff Saturday (if posting on Saturday) or Resource

---

**Title:** I made 145+ free browser-based developer tools with REST API access, no signup needed

**Body:**

I keep dozens of utility sites bookmarked for everyday dev tasks (Base64 encode, JSON format, UUID generate, etc.). Got tired of bouncing between them, so I built a single site with 145+ tools that all work in the browser AND as REST APIs.

Some of the tools:

- JSON formatter, validator, minifier
- Base64 / Base32 / Base58 encode and decode
- QR code generator
- UUID v4 generator
- Hash generator (MD5, SHA256, SHA512)
- JWT decoder
- DNS lookup (A, MX, NS, TXT records)
- WHOIS lookup
- Regex tester
- Markdown to HTML converter
- Color converter (HEX, RGB, HSL)
- Cron expression parser
- URL encoder/decoder
- Aspect ratio calculator
- Binary/decimal/hex converters
- API tester
- Fake data generator (names, emails, addresses for testing)

Every tool has a browser UI and a corresponding API endpoint. All CORS-enabled, so you can call them from client-side JS.

Quick example:

```bash
# Generate a UUID
curl https://troops-submission-what-stays.trycloudflare.com/api/uuid/generate

# Base64 encode
curl -X POST https://troops-submission-what-stays.trycloudflare.com/api/base64/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world"}'

# DNS lookup
curl "https://troops-submission-what-stays.trycloudflare.com/api/dns/lookup?domain=example.com"
```

No signup, no API key for the free tier (rate limited to 100 calls/day per IP).

There is also an MCP server so AI coding assistants (Claude, Cursor, etc.) can use all the tools natively.

Site: https://troops-submission-what-stays.trycloudflare.com
GitHub: https://github.com/COSAI-Labs/make-money-30day-challenge

What tools do you wish existed that I should add?
