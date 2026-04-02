# Reddit Post: r/sideproject

**Title:** Day 2 of shipping 230+ free API endpoints for developers

**Body:**

Built a developer toolkit with 230+ REST API endpoints. All free, no signup.

The idea: every developer has the same 10-20 utility sites bookmarked (JSON formatters, Base64 encoders, UUID generators, etc.). I packaged all of them into one API.

What's included:
- Data: JSON format/validate, Base64, CSV/JSON conversion, XML parsing
- Security: Hashing (MD5/SHA), UUID gen, JWT decode, password gen
- Web: DNS lookup, WHOIS, domain intel, web scraping, screenshots
- Code: Code review, regex gen, Dockerfile gen, SQL formatting
- Content: QR codes, fake data, markdown, text analysis, PDF tools
- SEO: Site analysis, sitemap parsing, meta extraction

Tech stack: Python/FastAPI on a VPS with Cloudflare tunnel.

Also built an MCP server so AI coding agents (Claude, Cursor, Windsurf) can use all these tools natively.

No API key needed for the free tier (100 calls/day).

https://toolpipe.dev

What would you add to a developer utility API?
