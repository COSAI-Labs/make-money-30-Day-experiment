# Reddit Post: r/sideproject

**Subreddit:** r/sideproject
**Type:** Text post

---

**Title:** Day 3 of building an autonomous developer toolkit: 145+ tools and counting

**Body:**

I have been building a developer utility platform as a challenge to ship as fast as possible. Day 3 status: 145+ tools live, all with browser UIs and REST API access.

The concept: one site where you can do all the small dev tasks you normally need 20 different bookmarks for. JSON formatting, Base64 encoding, UUID generation, hashing, DNS lookups, regex testing, color conversion, and about 130 more.

What makes it different from the hundreds of "dev tools" sites:

1. Every tool also works as an API endpoint. No auth required for free tier.
2. All endpoints are CORS-enabled, so you can use them from browser JS.
3. Built an MCP server so AI agents (Claude, Cursor, Windsurf) can use all 145+ tools.
4. The whole thing runs on a single VPS with a Cloudflare tunnel.

Tech stack: Python/FastAPI backend, vanilla JS frontend, Cloudflare tunnel for HTTPS.

Most used tools so far (based on server logs):
- JSON formatter
- Base64 encode/decode
- UUID generator
- QR code generator
- Hash generator

Next up: webhook testing, cron monitoring, and more AI-focused tools.

Live: https://troops-submission-what-stays.trycloudflare.com
Source: https://github.com/COSAI-Labs/make-money-30day-challenge

Would love feedback. What utility tools do you reach for most often?
