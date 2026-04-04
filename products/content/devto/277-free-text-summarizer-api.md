---
title: "Free Text Summarizer API: Extractive Summarization via REST"
published: false
tags: nlp, api, textprocessing, tools
---

Summarize text programmatically with ToolPipe's free text summarizer API.

## Usage

```bash
curl -X POST https://toolpipe.dev/api/text/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here...", "sentences": 3}'
```

## Features

- Extractive summarization
- Configurable summary length
- Key sentence extraction
- No API key required

Great for content processing pipelines, RSS feed summarization, or article previews.

**Try it**: [toolpipe.dev](https://toolpipe.dev) - 240+ free developer APIs.
