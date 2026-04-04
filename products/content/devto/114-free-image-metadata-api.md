---
title: "Free Image Metadata Extractor API: EXIF and GPS Data via REST"
published: false
tags: ["api", "images", "photography", "webdev"]
---

Extract EXIF, GPS, and metadata from images via REST API.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/image/metadata \
  -F "image=@photo.jpg"
```

## Extracted Data

- EXIF (camera, lens, settings)
- GPS coordinates
- Image dimensions and format
- Color space and bit depth
- Creation date

Use cases: photo management, privacy auditing (check for GPS leaks), asset management, forensic analysis.

Free at [toolpipe.dev](https://toolpipe.dev) - no signup required.
