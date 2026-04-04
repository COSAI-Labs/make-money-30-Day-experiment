---
title: "Free Text Analysis API - Word Count, Readability, Keywords"
tags: text, nlp, api, webdev
canonical_url: https://toolpipe.dev
---

Analyze text for word count, readability, sentiment, and keywords.

```bash
curl -X POST https://toolpipe.dev/text/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your content here"}'
```

Returns word count, reading time, Flesch-Kincaid score, and keyword extraction.

**Try it:** [toolpipe.dev](https://toolpipe.dev)
