# ToolPipe API

Multi-endpoint developer utility API. Fast, reliable, no auth required for free tier.

## Endpoints

- POST /qr/generate - Generate QR codes (PNG)
- GET /meta/extract - Extract URL metadata (OG tags, title, favicon)
- POST /markdown/to-html - Convert Markdown to HTML
- POST /text/analyze - Word count, reading time, Flesch score
- POST /hash/generate - Generate MD5, SHA256, etc.
- POST /image/resize - Resize images by URL
- POST /json/to-csv - Convert JSON arrays to CSV
- GET /uuid/generate - Generate UUIDs (v1, v4)
- GET /dns/lookup - DNS resolution
- GET /color/convert - Hex to RGB/HSL
- POST /base64 - Base64 encode/decode

## Revenue Model

- Free tier: 100 requests/minute (rate limited)
- Pro tier: $9.99/month via RapidAPI (higher limits, priority)
- Enterprise: $49.99/month (custom endpoints, SLA)

## Deployment

Running on port 8080 via PM2.
