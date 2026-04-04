---
title: "Free package.json Generator API"
published: false
tags: ["nodejs", "api", "javascript", "webdev"]
---

## Free package.json Generator API

Generate package.json files for Node.js projects via API.

### Endpoint

```
POST https://toolpipe.dev/api/generate/package-json
```

### Example

```bash
curl -X POST https://toolpipe.dev/api/generate/package-json \
  -H "Content-Type: application/json" \
  -d '{"name": "my-app", "description": "My Node.js app", "type": "module"}'
```

No signup required. Part of 240+ free tools at [toolpipe.dev](https://toolpipe.dev).
