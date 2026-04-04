---
title: "Free Base64 Encode/Decode API for Developers"
published: false
tags: ["api", "base64", "encoding", "webdev"]
---

## Free Base64 API

Encode and decode Base64 strings via a simple REST API. No signup, no dependencies.

### Endpoint

```
POST https://toolpipe.dev/base64
```

### Request Body

```json
{
  "data": "Hello World",
  "action": "encode"
}
```

Set `action` to `"encode"` or `"decode"`.

### Example

```bash
# Encode
curl -X POST https://toolpipe.dev/base64 \
  -H "Content-Type: application/json" \
  -d '{"data": "Hello World", "action": "encode"}'

# Decode
curl -X POST https://toolpipe.dev/base64 \
  -H "Content-Type: application/json" \
  -d '{"data": "SGVsbG8gV29ybGQ=", "action": "decode"}'
```

### When to Use

- Quick encoding in shell scripts
- CI/CD pipeline transformations
- Serverless functions without heavy dependencies
- Cross-language encoding consistency

Part of 70+ free developer tools at [toolpipe.dev](https://toolpipe.dev).
