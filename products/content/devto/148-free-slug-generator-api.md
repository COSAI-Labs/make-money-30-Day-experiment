---
title: "Free URL Slug Generator API: SEO-Friendly Slugs in One Call"
published: false
tags: ["seo", "api", "webdev", "urlslug"]
canonical_url: "https://toolpipe.dev"
---

Generating URL slugs seems simple until you deal with unicode, special characters, and edge cases. ToolPipe handles it.

## Usage

```bash
curl -X POST https://toolpipe.dev/text/slugify \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World! This is a Test 123"}'
```

Returns: `hello-world-this-is-a-test-123`

### Features
- Unicode normalization
- Transliteration (accented characters to ASCII)
- Configurable separator
- Max length option
- Handles CJK characters

### Part of 120+ free developer tools

Text analysis, markdown conversion, lorem ipsum generation, and 116 more. All free via REST API or MCP server.

```bash
npx @cosai-labs/toolpipe-mcp-server
```

[toolpipe.dev](https://toolpipe.dev)
