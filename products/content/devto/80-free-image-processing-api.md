---
title: "Free Image Processing API: Resize, Convert, and Optimize Images via REST"
published: false
tags: api, images, webdev, optimization
series: "Free Developer APIs"
---

Need to resize images on the fly? Convert between formats? ToolPipe's image API handles it all with a simple REST call.

## Resize an Image

```bash
curl -X POST https://toolpipe.dev/image/resize \
  -F "image=@photo.jpg" \
  -F "width=800" \
  -F "height=600" \
  -o resized.jpg
```

## Convert Formats

```bash
curl -X POST https://toolpipe.dev/image/convert \
  -F "image=@photo.png" \
  -F "format=webp" \
  -o output.webp
```

## Features

- Resize to exact dimensions or proportional scaling
- Convert between PNG, JPG, WebP, GIF, TIFF
- No signup, no API key for free tier
- Handles files up to 10MB

## Full Toolkit

ToolPipe provides 55+ free developer APIs at [toolpipe.dev](https://toolpipe.dev). QR codes, PDF tools, hashing, DNS, SSL checking, and much more.

MCP Server for AI agents: `npx @cosai-labs/toolpipe-mcp-server` (120+ tools)
