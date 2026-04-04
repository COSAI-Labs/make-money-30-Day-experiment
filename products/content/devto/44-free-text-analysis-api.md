---
title: "Free Text Analysis API: Word Count, Readability, Sentiment"
published: false
tags: nlp, api, textprocessing, devtools
---

Analyze any text for readability, sentiment, and statistics via REST API.

```bash
curl -X POST https://toolpipe.dev/text/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your content here for analysis."}'
```

## Returns
- Word count, sentence count, paragraph count
- Reading time estimate
- Readability score (Flesch-Kincaid)
- Sentiment analysis (positive/negative/neutral)
- Keyword extraction

Perfect for content management systems, SEO tools, and editorial workflows.

Free, no API key required. [toolpipe.dev](https://toolpipe.dev)
