---
title: "Free PDF Watermark API - Add Watermarks to PDFs Programmatically"
published: false
tags: ["api", "pdf", "webdev", "tools"]
---

Need to add watermarks to PDFs in your application? ToolPipe provides a free PDF Watermark API that does this with a single REST call.

## API Endpoint

```
POST https://toolpipe.dev/pdf/watermark
Content-Type: multipart/form-data

Parameters:
- file: Your PDF file
- text: Watermark text
- opacity: 0.1 to 1.0 (default 0.3)
```

## Other PDF Tools

ToolPipe also provides free APIs for:
- PDF merge (`/pdf/merge`)
- PDF split (`/pdf/split`)
- PDF compress (`/pdf/compress`)
- PDF protect with password (`/pdf/protect`)
- PDF unlock (`/pdf/unlock`)
- PDF rotate (`/pdf/rotate`)

## Get Started

No signup required. Free tier: 100 calls/day. Full documentation: [toolpipe.dev/docs](https://toolpipe.dev/docs)

70+ developer tools available at [toolpipe.dev](https://toolpipe.dev).
