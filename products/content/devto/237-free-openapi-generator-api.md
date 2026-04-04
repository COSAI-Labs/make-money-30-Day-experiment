---
title: "Free OpenAPI Specification Generator API"
published: false
tags: openapi, swagger, api, webdev
canonical_url: https://toolpipe.dev/api
---

Generate OpenAPI/Swagger specifications from API descriptions.

```bash
curl -X POST https://toolpipe.dev/api/openapi/generate \
  -H "Content-Type: application/json" \
  -d '{"title": "My API", "endpoints": [{"path": "/users", "method": "GET"}]}'
```

**70+ free tools at [toolpipe.dev/api](https://toolpipe.dev/api)**
