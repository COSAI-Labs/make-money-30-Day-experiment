---
title: "Free SSL Certificate Checker API: Monitor Cert Expiry via REST"
published: false
tags: ssl, security, devops, api
---

Monitor SSL certificate expiration across all your domains with a simple API call.

```bash
curl "https://toolpipe.dev/ssl/check?domain=github.com"
```

Returns:
- Certificate issuer and subject
- Expiration date
- Days until expiry
- Protocol version
- Chain validity

Perfect for:
- Automated monitoring dashboards
- CI/CD pipeline checks
- DevOps alerting systems
- Security audits

Part of 120+ free developer tools at [toolpipe.dev](https://toolpipe.dev).

Also available as an MCP server for AI coding assistants:
```bash
npx @cosai-labs/toolpipe-mcp-server
```
