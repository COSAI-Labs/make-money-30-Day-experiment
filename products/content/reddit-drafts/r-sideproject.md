# Title: Built 220+ developer API endpoints as a side project. Here's what I learned.

## Body:

I set out to build a "Swiss Army knife" API for developers. The goal: every common dev utility as a simple REST endpoint, zero signup required.

**The result:** 220+ endpoints covering JSON/XML processing, QR codes, hashing, UUID generation, DNS lookups, WHOIS, web scraping, PDF tools, SEO analysis, fake data generation, and more.

**What went right:**
- FastAPI made it incredibly fast to ship endpoints
- Each tool is self-contained, easy to add new ones
- Free tier with no auth means zero friction for users
- Also works as an MCP server so AI agents can use it

**What I'd do differently:**
- Start with fewer, more polished tools instead of going wide immediately
- Get a proper domain earlier (still on a Cloudflare tunnel URL)

**Live API:** https://troops-submission-what-stays.trycloudflare.com
**Docs:** https://troops-submission-what-stays.trycloudflare.com/docs
**GitHub:** https://github.com/COSAI-Labs/make-money-30day-challenge

Curious if anyone else has built utility APIs like this. What's your experience with getting developer adoption?
