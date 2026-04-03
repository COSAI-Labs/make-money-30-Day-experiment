# Reddit Post: r/selfhosted

**Subreddit:** r/selfhosted
**Type:** Text post

---

**Title:** Self-hosted developer utility API: 240+ tools on a single VPS behind Cloudflare Tunnel

**Body:**

I built a self-hosted developer toolkit that runs 240+ utility tools on a single Debian VPS. Everything goes through a Cloudflare Tunnel for HTTPS, no port forwarding needed.

Stack:
- Python/FastAPI serving all API endpoints
- Vanilla JS frontend for browser-based usage
- Cloudflare Tunnel for public HTTPS access
- PM2 for process management

Tools include: JSON formatting, Base64 encoding, UUID generation, hashing (MD5/SHA), DNS lookups, WHOIS, QR code generation, regex testing, JWT decoding, color conversion, cron parsing, and about 130 more.

Every tool works both as a web UI and as a REST API endpoint. No auth required, CORS-enabled.

Resource usage is surprisingly low. FastAPI handles the routing efficiently and most of these tools are CPU-light operations.

The whole project is open source: https://github.com/COSAI-Labs/make-money-30day-challenge

Live instance: https://toolpipe.dev

If anyone wants to self-host it, the FastAPI server and all endpoints are in the repo. Happy to help with setup questions.
