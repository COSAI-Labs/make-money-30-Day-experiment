---
title: "Free IP Lookup API - Get Public IP and Geolocation Data"
published: false
tags: ["api", "networking", "webdev", "tools"]
---

Find your public IP address or look up geolocation data for any IP with ToolPipe's free API.

## Endpoints

```
GET https://toolpipe.dev/ip/my
Response: {"ip": "203.0.113.42"}

GET https://toolpipe.dev/ip/lookup?ip=8.8.8.8
Response: {"ip": "8.8.8.8", "country": "US", "city": "Mountain View", "org": "Google LLC"}
```

## Use Cases

- Server configuration and deployment
- Geo-targeting content
- Security logging
- Network diagnostics

No signup. Free tier: 100 calls/day. Docs: [toolpipe.dev/docs](https://toolpipe.dev/docs)
