---
title: "Free Regex Tester API: Validate Patterns and Get Match Results via REST"
published: false
tags: regex, api, testing, tools
---

Test regex patterns programmatically with match positions and capture groups.

```bash
curl -X POST https://toolpipe.dev/api/regex/test \
  -H "Content-Type: application/json" \
  -d '{"pattern": "\\d{3}-\\d{4}", "text": "Call 555-1234 or 666-5678", "flags": "g"}'
```

Returns all matches, positions, and capture groups in JSON. Great for CI/CD validation and building dev tools.

[Full docs](https://toolpipe.dev/docs)
