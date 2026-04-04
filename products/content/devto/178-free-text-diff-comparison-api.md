---
title: "Free Text Diff and Comparison API for Developers"
published: false
tags: api, webdev, tools, productivity
---

## Compare Texts Programmatically

Get unified diffs, similarity scores, and character-level change detection through a simple API.

### Quick Start

```bash
curl -X POST https://toolpipe.dev/text/diff \
  -H "Content-Type: application/json" \
  -d '{"text1": "Hello World", "text2": "Hello World!"}'
```

### Features

- Unified diff format output
- Line-by-line comparison
- Character-level change detection
- Jaccard, cosine, and character similarity
- Works with any text content

Also available: text summarization, keyword extraction, language detection, and 115+ more tools.

[toolpipe.dev](https://toolpipe.dev) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
