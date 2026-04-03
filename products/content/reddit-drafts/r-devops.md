# Reddit Post: r/devops

**Subreddit:** r/devops
**Type:** Text post

---

**Title:** Free API for quick DNS, SSL, WHOIS, and HTTP checks (240+ dev tool endpoints, no auth)

**Body:**

Built a utility API that handles a bunch of the quick checks I used to do manually or with random websites. Thought it might be useful for others doing ops work.

Some of the endpoints I use most:

```bash
# DNS lookup with record type
curl "https://toolpipe.dev/api/dns/lookup?domain=example.com&type=MX"

# SSL certificate check (expiry, issuer, chain)
curl "https://toolpipe.dev/api/ssl/check?domain=example.com"

# WHOIS lookup
curl "https://toolpipe.dev/api/whois/lookup?domain=example.com"

# HTTP headers inspection
curl "https://toolpipe.dev/api/http/headers?url=https://example.com"

# IP geolocation
curl "https://toolpipe.dev/api/ip/geo?ip=8.8.8.8"
```

No API key, no signup. Just hit the endpoint. CORS enabled so it works from scripts, CI pipelines, or browser-based dashboards.

There are 240+ endpoints total covering text processing, hashing, PDF tools, QR codes, data generation, and more, but the network/infra tools are probably most relevant here.

Full docs (Swagger): https://toolpipe.dev/docs
Live: https://toolpipe.dev
GitHub: https://github.com/COSAI-Labs/make-money-30day-challenge

Also available as an MCP server for AI coding agents: `npx @cosai-labs/toolpipe-mcp-server`

What monitoring or infra checks would you want as a simple curl command?
