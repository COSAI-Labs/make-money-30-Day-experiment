---
title: "Free User Agent Parser API - Detect Browsers and Devices"
published: false
tags: ["api", "webdev", "analytics", "tools"]
---

Parse user agent strings to detect browsers, operating systems, and device types with ToolPipe's free API.

## API Endpoint

```
GET https://toolpipe.dev/useragent/parse?ua=Mozilla/5.0...

Response:
{
  "browser": "Chrome",
  "version": "120.0",
  "os": "Windows 10",
  "device": "Desktop"
}
```

## Use Cases

- Analytics dashboards
- Browser-specific feature detection
- Device-targeted content
- Bot detection

No signup required. Free tier: 100 calls/day. Full docs: [toolpipe.dev/docs](https://toolpipe.dev/docs)
