---
title: "Free Content Security Policy (CSP) Header Generator API"
published: false
tags: security, api, webdev, devops
canonical_url: https://toolpipe.dev/api
---

Generate Content Security Policy headers for your web applications with ToolPipe's free API.

```bash
curl -X POST https://toolpipe.dev/api/security/csp-generate \
  -H "Content-Type: application/json" \
  -d '{"directives": {"default-src": ["self"], "script-src": ["self", "cdn.example.com"]}}'
```

**70+ free developer tools at [toolpipe.dev/api](https://toolpipe.dev/api)**
