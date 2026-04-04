---
title: "Free Security Headers Checker API: Audit Any Website"
published: false
tags: security, api, webdev, devops
---

Check HTTP security headers for any URL with ToolPipe's free security headers API.

## Usage

```bash
curl "https://toolpipe.dev/api/security-headers?url=https://example.com"
```

## What It Checks

- Content-Security-Policy
- Strict-Transport-Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

Returns a score and specific recommendations for each header.

**Try it**: [toolpipe.dev](https://toolpipe.dev) - 240+ free developer APIs.
