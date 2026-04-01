# ToolPipe API

Free developer utility APIs. 55+ endpoints for QR codes, text analysis, PDF processing, image manipulation, DNS lookup, and more.

## Quick Start

No API key required for the free tier.

```bash
# Generate a QR code
curl -X POST https://toolpipe.dev/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"data": "https://example.com"}'

# Extract metadata from a URL
curl "https://toolpipe.dev/meta/extract?url=https://github.com"

# Analyze text
curl -X POST https://toolpipe.dev/text/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your content here"}'
```

## Endpoints

### Core API
- `POST /qr/generate` - Generate QR codes (PNG)
- `GET /meta/extract?url=` - Extract Open Graph metadata
- `POST /text/analyze` - Word count, readability, sentiment
- `POST /markdown/to-html` - Markdown to HTML
- `POST /hash/generate` - MD5, SHA256, SHA512
- `POST /image/resize` - Resize images
- `POST /image/convert` - Convert image formats
- `POST /json/to-csv` - JSON to CSV
- `GET /uuid/generate` - Generate UUIDs
- `GET /dns/lookup?domain=` - DNS records
- `GET /color/convert?hex=` - Color conversion
- `POST /base64` - Base64 encode/decode

### PDF Tools
- `POST /pdf/merge` - Merge PDFs
- `POST /pdf/split` - Split PDF by pages
- `POST /pdf/compress` - Compress PDF
- `POST /pdf/rotate` - Rotate pages
- `POST /pdf/watermark` - Add watermark
- `POST /pdf/protect` - Password protect
- `POST /pdf/extract-text` - Extract text

### URL Shortener
- `POST /s/create` - Create short URL
- `GET /s/{code}` - Redirect
- `GET /s/{code}/stats` - Click analytics

### Network Tools
- `GET /ip/lookup?ip=` - IP geolocation
- `GET /ip/my` - Your public IP
- `GET /down/check?url=` - Is website down?
- `GET /seo/analyze?url=` - SEO audit

## Rate Limits
- Free: 100 req/min
- Pro: 1,000 req/min ($9.99/mo)
- Enterprise: Unlimited ($49.99/mo)

## SDKs
Python and JavaScript client libraries in `../digital-products/api-starter-kit/`.
