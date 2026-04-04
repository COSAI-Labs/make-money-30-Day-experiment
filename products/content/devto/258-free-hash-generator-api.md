---
title: "Free Hash Generator API - MD5, SHA256, SHA512 via REST"
tags: hash, security, api, webdev
canonical_url: https://toolpipe.dev
---

Generate cryptographic hashes with a simple API call.

```bash
curl -X POST https://toolpipe.dev/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "algorithm": "sha256"}'
```

Supports MD5, SHA256, SHA512. No API key needed.

**Try it:** [toolpipe.dev](https://toolpipe.dev)
