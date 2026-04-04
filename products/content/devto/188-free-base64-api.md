---
title: "Free Base64 Encode/Decode API for Developers"
tags: base64,api,encoding,webdev
canonical_url: https://toolpipe.dev
published: false
---

Encode and decode Base64 via API. Supports standard and URL-safe variants.

## Examples

```bash
# Encode
curl -X POST https://toolpipe.dev/base64/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World!"}'

# Decode
curl -X POST https://toolpipe.dev/base64/decode \
  -H "Content-Type: application/json" \
  -d '{"encoded": "SGVsbG8sIFdvcmxkIQ=="}'
```

## Features

- Standard Base64 (RFC 4648)
- URL-safe Base64 (RFC 4648 Section 5)
- Binary content support
- Proper UTF-8 handling
- Batch encode/decode

## When You Need an API

Shell scripts, CI pipelines, serverless functions, and cross-platform tools benefit from a consistent Base64 API rather than platform-specific implementations.

Free at [toolpipe.dev](https://toolpipe.dev). Part of 120+ developer utility APIs.
