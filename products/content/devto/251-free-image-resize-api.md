---
title: "Free Image Resize API - Resize Images via REST"
tags: image, api, tools, webdev
canonical_url: https://toolpipe.dev
---

Resize images programmatically with a REST API. Supports PNG, JPEG, WebP.

## Usage

```bash
curl -X POST https://toolpipe.dev/image/resize \
  -F "file=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -o resized.jpg
```

Also: `POST /image/convert` for format conversion and `POST /qr/generate` for QR codes.

**Try it:** [toolpipe.dev](https://toolpipe.dev)
