---
title: "Check If Any Website Is Up: Free Uptime Monitoring API"
published: false
tags: devops, monitoring, api, tools
canonical_url: https://toolpipe.dev
---

Need to check if a website is up from your backend or script? ToolPipe's uptime monitoring API returns status, response time, SSL info, and DNS resolution time.

## Quick Check

```bash
curl "https://toolpipe.dev/uptime/check?url=https://example.com"
```

## Response Includes

- HTTP status code
- Response time (ms)
- SSL certificate validity and expiry
- DNS resolution time
- Redirect chain (if any)

## Use Cases

- Build a status page for your services
- Monitor third-party API availability
- Pre-deploy health checks in CI/CD
- Alert systems for critical endpoints

## Also Available via MCP

238 developer tools including uptime monitoring, accessible to AI agents:

```bash
npx @cosai-labs/toolpipe-mcp-server
```

- **API**: [toolpipe.dev](https://toolpipe.dev)
- **npm**: [@cosai-labs/toolpipe-mcp-server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
