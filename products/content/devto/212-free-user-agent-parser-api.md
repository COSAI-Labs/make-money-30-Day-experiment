---
title: "Free User Agent Parser API - Browser and Device Detection"
published: false
tags: ["api", "useragent", "analytics", "webdev"]
---

## Free User Agent Parser API

Parse user agent strings into structured data: browser, OS, device type, and bot detection.

### Endpoint

```
GET https://toolpipe.dev/useragent/parse
```

Pass `ua` as a query parameter, or omit it to parse the requesting client's user agent.

### Example

```bash
curl "https://toolpipe.dev/useragent/parse?ua=Mozilla/5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)"
```

### Returns

- Browser name and version
- Operating system and version
- Device type (desktop, mobile, tablet)
- Bot/crawler detection

### Use Cases

- Server-side analytics
- Feature flag targeting by browser
- Bot filtering in API gateways
- Log enrichment pipelines

No signup required. Free at [toolpipe.dev](https://toolpipe.dev).
