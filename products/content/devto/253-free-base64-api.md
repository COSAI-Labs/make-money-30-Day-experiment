---
title: "Free Base64 Encode/Decode API for Developers"
tags: base64, api, encoding, webdev
canonical_url: https://toolpipe.dev
---

Encode and decode Base64 strings via REST. No dependencies needed.

## Encode
```bash
curl -X POST https://toolpipe.dev/base64 \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "action": "encode"}'
```

## Decode
```bash
curl -X POST https://toolpipe.dev/base64 \
  -H "Content-Type: application/json" \
  -d '{"text": "SGVsbG8gV29ybGQ=", "action": "decode"}'
```

**Try it:** [toolpipe.dev](https://toolpipe.dev)
