---
title: "Free JSON Diff API - Compare Two JSON Objects Instantly"
published: false
tags: ["json", "api", "webdev", "javascript"]
canonical_url: "https://toolpipe.dev"
---

## Compare JSON Objects via API

Need to compare API responses, config files, or database records? ToolPipe's JSON Diff API shows exactly what changed.

### Endpoint

```
POST https://toolpipe.dev/api/json/diff
```

### Example

```bash
curl -X POST https://toolpipe.dev/api/json/diff \
  -H "Content-Type: application/json" \
  -d '{"a": {"name": "v1", "count": 5}, "b": {"name": "v2", "count": 5, "new": true}}'
```

### Returns

- Added fields
- Removed fields  
- Modified fields with before/after values
- Nested object comparison

Free: 100 calls/day, no signup. Part of 70+ APIs at [ToolPipe](https://toolpipe.dev).
