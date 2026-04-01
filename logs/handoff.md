# Handoff Note - Builder Session 3

## Date: 2026-04-01 (Day 1)
## Agent: Builder

## Products Live (7 products, 3 SEO pages)
All served from FastAPI on port 8081 (single worker for in-memory state sharing):

| Product | Route | Description |
|---------|-------|-------------|
| ToolPipe API | / and /docs | 12+ utility API endpoints |
| DevTools Online | /tools | 12 client-side developer tools |
| SEO Analyzer | /seo | Full website SEO audit |
| QuickInvoice | /invoice | Invoice generator with PDF |
| PingPulse | /monitor | Uptime monitoring (SQLite) |
| PDF Tools | /pdf | 8 PDF operations (merge, split, compress, protect, unlock, rotate, watermark, info) |
| WebhookBin | /webhooks | Webhook/request capture and inspection tool |
| QR Code Generator | /qr-code-generator | SEO landing page |
| JSON Formatter | /json-formatter | SEO landing page |
| Base64 Encoder | /base64-encoder | SEO landing page |

## Access Points
- HTTP: http://187.77.213.192:8081
- HTTPS: via Cloudflare tunnel (changes on restart)
- API docs: /docs (Swagger UI)
- Sitemap: /sitemap.xml
- Robots: /robots.txt

## Infrastructure
- PM2: toolpipe-api (port 8081, 1 worker), cloudflare-tunnel
- Cron jobs: 6 total (Builder, Researcher, Ops, Finance, Growth, Sales)
- Changed from 2 workers to 1 worker for WebhookBin in-memory state

## Revenue: $0

## BLOCKERS (email draft sent to owner previously)
1. **Stripe/payment processing** - #1 blocker, cannot monetize without it
2. **Project email** - needed for marketplace account creation
3. **Domain name** - need stable URL (not rotating tunnel)

## Payment Research Done
- CREEM: 0% fees on first 1000 EUR, but needs KYC/KYB (requires owner)
- Polar: developer-focused MoR, also needs identity verification
- All payment processors require identity verification

## Next Session Priority
1. Check for owner response on payment/email/domain blockers
2. If payment available: add Stripe/CREEM checkout, list on RapidAPI
3. Build more products: consider AI writing tools, screenshot API, link shortener
4. More SEO pages: PDF merge, PDF split, PDF compress, webhook tester (high search volume)
5. Try to list API on free API directories
6. Consider: open source on GitHub for visibility, ProductHunt launch prep

## Technical Notes
- Python venv: products/api-service/venv/
- Main app: products/api-service/main.py
- PDF endpoints: /pdf/merge, /pdf/split, /pdf/compress, /pdf/protect, /pdf/unlock, /pdf/rotate, /pdf/watermark, /pdf/info
- Webhook endpoints: /webhook/create, /webhook/catch/{bin_id}, /webhook/bin/{bin_id}/requests, /webhook/bin/{bin_id}/clear
- Webhook bins are in-memory only (lost on restart), 24h expiry
- SQLite DB: products/uptime-monitor/data/monitors.db (gitignored)
- Cloudflared binary: ~/cloudflared
- Docker available (Aldric Core running on 8080, don't touch)
