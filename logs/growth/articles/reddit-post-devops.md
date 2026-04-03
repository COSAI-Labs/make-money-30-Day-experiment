# Reddit Post: r/devops

**Title:** Free API for DevOps utilities: Docker Compose gen, Nginx config, SSL check, DNS lookup, cron parser

**Body:**

Made a collection of 220+ developer/DevOps utility APIs. All free, no auth needed. Some DevOps-specific ones:

**Infrastructure:**
- Docker Compose generator: POST your services, get a docker-compose.yml
- Nginx config generator: reverse proxy, SSL, caching configs
- .gitignore generator: per-language/framework templates
- Cron expression parser: validate and explain cron schedules

**Monitoring/Debugging:**
- SSL certificate checker: expiry, chain, issuer details
- DNS lookup: A, AAAA, MX, NS, TXT, CNAME, SOA records
- WHOIS lookup: domain registration info
- HTTP header analyzer: security headers audit
- IP geolocation: GeoIP data

**Security:**
- Hash generator: MD5, SHA-1, SHA-256, SHA-512
- JWT decoder: decode without sending to jwt.io
- CSP header generator
- Password generator

All REST API with JSON responses. Use in scripts:

```bash
# Check SSL cert expiry
curl -s "toolpipe.dev/ssl-checker?domain=yoursite.com" | jq '.expiry'

# Generate Docker Compose
curl -s "toolpipe.dev/docker-compose-generator" -X POST -d '...'

# Parse cron
curl -s "toolpipe.dev/cron-parser?expression=0+*/6+*+*+*" | jq .
```

https://toolpipe.dev

Also has an MCP server for AI coding agents if that's your thing.
