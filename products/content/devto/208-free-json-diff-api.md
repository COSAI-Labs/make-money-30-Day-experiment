---
title: "Free JSON Diff API: Compare Two JSON Objects via REST"
published: false
tags: ["api", "json", "testing", "webdev"]
canonical_url: "https://toolpipe.dev"
---

# Free JSON Diff API

Compare two JSON objects and get a structured diff. Perfect for testing, debugging, and config management.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/json/diff \
  -H "Content-Type: application/json" \
  -d '{"json1": {"name": "Alice", "age": 30}, "json2": {"name": "Alice", "age": 31}}'
```

## Diff Output

- Added keys/values
- Removed keys/values
- Modified values with before/after
- Nested object comparison
- Array element tracking

## Use Cases

- API response testing in CI/CD
- Configuration drift detection
- Schema validation
- Data migration verification

[https://toolpipe.dev](https://toolpipe.dev) - 120+ free developer APIs
