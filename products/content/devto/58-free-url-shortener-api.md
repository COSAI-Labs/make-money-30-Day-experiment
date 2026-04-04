---
title: "Free URL Shortener API: Create Short Links Programmatically"
published: false
tags: url, api, webdev, tools
---

Shorten URLs via REST API. No signup, no rate limits on free tier.

```bash
curl -X POST https://toolpipe.dev/url/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path"}'
```

Features: custom aliases, click analytics, QR code generation.

[ToolPipe](https://toolpipe.dev) - 120+ developer utility APIs. MIT License.
