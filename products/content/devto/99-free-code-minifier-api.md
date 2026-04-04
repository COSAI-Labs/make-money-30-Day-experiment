---
title: "Free Code Minifier API: Minify JS, CSS, HTML via REST"
published: false
tags: ["javascript", "webdev", "api", "productivity"]
canonical_url: "https://toolpipe.dev"
---

# Free Code Minifier API

Need to minify JavaScript, CSS, or HTML in your build pipeline? ToolPipe offers a free REST API that handles it.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/code/minify \
  -H "Content-Type: application/json" \
  -d '{"code": "function hello() { return \"world\"; }", "language": "javascript"}'
```

Returns minified code with size reduction stats. No signup, no API key.

## Why Use an API for Minification?

- CI/CD pipelines that need minification without installing toolchains
- Serverless functions that process code on the fly
- Quick one-off minification without setting up webpack/esbuild

## 120+ More Tools

ToolPipe has 120+ free developer utility endpoints: JSON formatter, SQL formatter, QR codes, hash generators, UUID, DNS lookup, and more.

**Try it free:** [toolpipe.dev](https://toolpipe.dev)
