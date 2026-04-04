---
title: "Free HTTP Status Code Checker API: Test Any URL's Response via REST"
published: false
tags: ["api", "webdev", "monitoring", "devops"]
---

Check HTTP status codes for any URL with a simple API call.

## Quick Start

```bash
curl "https://toolpipe.dev/http/status?url=https://example.com"
```

## Response

```json
{
  "url": "https://example.com",
  "status": 200,
  "statusText": "OK",
  "responseTime": 145,
  "headers": {}
}
```

## Use Cases

- Uptime monitoring
- Link checking / broken link detection
- Redirect chain analysis
- CI/CD health checks

Free at [toolpipe.dev](https://toolpipe.dev) - 70+ developer APIs, no signup required.
