---
title: "Free Hash Generator API: MD5, SHA-256, SHA-512 via REST"
published: false
tags: security, hashing, api, devtools
---

Generate cryptographic hashes without crypto libraries.

```bash
curl -X POST https://toolpipe.dev/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "algorithm": "sha256"}'
```

Supports MD5, SHA-1, SHA-256, SHA-512. Free tier: 100 calls/day.

[ToolPipe](https://toolpipe.dev) - 120+ developer utility APIs.
