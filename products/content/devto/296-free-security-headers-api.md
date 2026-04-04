---
title: "Free Security Headers Checker API: Scan Any Website"
published: false
tags: ["security", "webdev", "api", "devops"]
canonical_url: "https://toolpipe.dev"
---

# Free Security Headers Checker API

Analyze HTTP security headers for any website via a free REST API. ToolPipe checks all major security headers and provides a grade with recommendations.

## Quick Start

```bash
curl https://toolpipe.dev/security/headers?url=https://example.com
```

Returns a detailed security analysis with header-by-header breakdown.

## Headers Checked

- Content-Security-Policy
- X-Frame-Options
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- X-XSS-Protection

## Use Cases

- CI/CD security gates
- Automated compliance scanning
- Security audit tooling
- DevSecOps pipelines

No signup required. MCP server: `npx @cosai-labs/toolpipe-mcp-server`

120+ more free tools at [toolpipe.dev](https://toolpipe.dev).
