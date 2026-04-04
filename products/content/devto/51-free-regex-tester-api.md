---
title: "Free Regex Tester API: Validate Patterns via REST"
published: false
tags: regex, api, testing, devtools
---

Test regular expressions programmatically without browser tools.

```bash
curl -X POST https://toolpipe.dev/regex/test \
  -H "Content-Type: application/json" \
  -d '{"pattern": "[a-z]+@[a-z]+\\.com", "text": "user@example.com"}'
```

Features: full regex syntax, match groups, captures, multi-string testing.

Free at [toolpipe.dev](https://toolpipe.dev) - 120+ developer utility APIs.
