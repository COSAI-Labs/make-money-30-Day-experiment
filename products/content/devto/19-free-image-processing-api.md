---
title: "Free Image Processing API: Resize, Convert & Optimize Without a Library"
published: false
tags: webdev, api, images, tools
canonical_url: https://toolpipe.dev
---

Tired of pulling in sharp, jimp, or imagemagick just to resize a thumbnail? ToolPipe's free Image Processing API handles resize, convert, and optimize via simple REST calls.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/image/resize \
  -F "image=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -o resized.jpg
```

## Endpoints

| Endpoint | What It Does |
|----------|-------------|
| `POST /image/resize` | Resize to any dimensions |
| `POST /image/convert` | Convert between PNG, JPG, WebP, GIF |

## Use Cases

- **Thumbnail generation** in your upload pipeline
- **Batch conversion** in CI/CD workflows
- **On-the-fly resize** for responsive images

## No Dependencies

No npm packages. No binary dependencies. Just HTTP.

## More Tools

ToolPipe has 55+ free API endpoints: QR codes, PDF tools, text analysis, DNS lookup, hashing, and more.

- **API**: [toolpipe.dev](https://toolpipe.dev)
- **MCP Server** (238 tools for AI agents): `npx @cosai-labs/toolpipe-mcp-server`
- **npm**: [@cosai-labs/toolpipe-mcp-server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
