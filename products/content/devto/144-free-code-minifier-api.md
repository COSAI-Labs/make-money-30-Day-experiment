---
title: "Free Code Minifier API: Minify JS, CSS, and HTML via REST"
published: false
tags: ["javascript", "css", "api", "performance"]
canonical_url: "https://toolpipe.dev"
---

Need to minify code in your build pipeline without installing toolchains? ToolPipe provides a free minification API.

## Usage

```bash
curl -X POST https://toolpipe.dev/code/minify \
  -H "Content-Type: application/json" \
  -d '{"code": "function hello() {\n  console.log(\"world\");\n}", "language": "javascript"}'
```

### Supported languages
- JavaScript / TypeScript
- CSS / SCSS
- HTML
- JSON

### Build pipeline integration

Add to your CI/CD as a minification step without local dependencies. Useful for serverless environments, quick prototypes, or edge functions.

### 120+ tools in one API

Code formatting, linting hints, diff, beautification, and 116 more tools. All free.

```bash
npx @cosai-labs/toolpipe-mcp-server
```

[toolpipe.dev](https://toolpipe.dev)
