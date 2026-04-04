---
title: "Free XML to JSON Converter API: Bidirectional Data Transformation"
published: false
tags: ["api", "xml", "json", "webdev"]
canonical_url: "https://toolpipe.dev"
---

# Free XML to JSON Converter API

Convert XML to JSON and JSON to XML via a free REST API. No authentication required.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/xml/to-json \
  -H "Content-Type: application/json" \
  -d '{"xml": "<root><name>Test</name><value>123</value></root>"}'
```

## Endpoints

- `POST /xml/to-json` - XML to JSON
- `POST /json/to-xml` - JSON to XML
- `POST /yaml/to-json` - YAML to JSON
- `POST /json/to-csv` - JSON to CSV

## Features

- Handles nested XML structures
- Attribute preservation
- Pretty-printed output
- Error reporting for malformed input

[https://toolpipe.dev](https://toolpipe.dev) - 120+ free developer APIs
