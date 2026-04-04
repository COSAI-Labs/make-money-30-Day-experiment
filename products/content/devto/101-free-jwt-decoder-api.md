---
title: "Free JWT Decoder API: Inspect Tokens Without Installing Libraries"
published: false
tags: ["security", "webdev", "api", "jwt"]
canonical_url: "https://toolpipe.dev"
---

# Free JWT Decoder API

Decode and inspect JWTs via a simple REST call. See the header, payload, expiration, and claims without installing any libraries.

```bash
curl -X POST https://toolpipe.dev/jwt/decode \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"}'
```

Returns structured JSON with decoded header, payload, and metadata. Free, no key needed.

**120+ free developer tools:** [toolpipe.dev](https://toolpipe.dev)
