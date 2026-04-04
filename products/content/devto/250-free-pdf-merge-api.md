---
title: "Free PDF Merge API - Combine PDFs with a Single API Call"
tags: pdf, api, tools, webdev
canonical_url: https://toolpipe.dev
---

Merge multiple PDF files into one with a simple REST API. No signup, no API key.

## Usage

```bash
curl -X POST https://toolpipe.dev/pdf/merge \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -o merged.pdf
```

## Full PDF Suite
- `POST /pdf/split` - Split by pages
- `POST /pdf/compress` - Reduce file size
- `POST /pdf/rotate` - Rotate pages
- `POST /pdf/watermark` - Add watermarks
- `POST /pdf/protect` - Password protection
- `POST /pdf/extract-text` - OCR text extraction

**Try it:** [toolpipe.dev](https://toolpipe.dev)
