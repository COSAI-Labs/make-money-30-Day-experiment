---
title: "Free Website Down Detector API - Check If Any Site Is Down"
published: false
tags: ["api", "monitoring", "devops", "tools"]
---

Check if any website is down with a simple API call. ToolPipe's Down Detector API returns status, response time, and availability instantly.

## API Endpoint

```
GET https://toolpipe.dev/down/check?url=example.com

Response:
{
  "url": "example.com",
  "is_down": false,
  "status_code": 200,
  "response_time_ms": 245
}
```

## Use Cases

- Build status pages for your services
- Monitor third-party dependencies
- Integrate availability checks into CI/CD pipelines
- Slack/Discord bot alerting

## Uptime Monitoring

Combine with the uptime monitoring API (`/monitor/add`, `/monitor/list`, `/monitor/run-all`) for continuous monitoring.

No signup required. Free tier: 100 calls/day. Docs: [toolpipe.dev/docs](https://toolpipe.dev/docs)
