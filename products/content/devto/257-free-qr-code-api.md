---
title: "Free QR Code Generator API - Generate QR Codes via REST"
tags: qrcode, api, tools, webdev
canonical_url: https://toolpipe.dev
---

Generate QR codes as PNG images with a single POST request.

```bash
curl -X POST https://toolpipe.dev/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"data": "https://your-site.com"}' \
  -o qrcode.png
```

Custom size, error correction levels. Encode URLs, text, WiFi, email, phone.

**Try it:** [toolpipe.dev](https://toolpipe.dev)
