---
title: "Free Website Down Checker API - Is It Down?"
published: false
tags: ["api", "monitoring", "uptime", "devops"]
---

## Free Website Down Checker API

Check if any website is up or down with a single API call.

### Endpoint

```
GET https://toolpipe.dev/down/check?url=https://github.com
```

### Response Includes

- Status (up or down)
- Response time in milliseconds
- HTTP status code
- SSL certificate details

### Example

```bash
curl "https://toolpipe.dev/down/check?url=https://google.com"
```

### Use Cases

- Uptime monitoring scripts
- CI/CD health gate checks
- Status page backends
- Slack/Discord alert integrations
- Cron-based availability monitoring

No signup. No API key. Part of 70+ free tools at [toolpipe.dev](https://toolpipe.dev).
