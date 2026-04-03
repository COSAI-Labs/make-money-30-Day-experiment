---
title: "220+ Free APIs Every Developer Should Bookmark"
published: false
description: "A curated list of 220+ free REST APIs for developers: JSON tools, QR codes, DNS lookups, code review, Docker generators, and more. No signup required."
tags: api, webdev, programming, free
cover_image: 
canonical_url: https://toolpipe.dev
---

I put together a collection of 220+ free REST APIs that cover the most common developer needs. All available at [toolpipe.dev](https://toolpipe.dev) with zero signup.

## Text & Data APIs

```bash
# Format JSON
curl -X POST https://toolpipe.dev/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"key\":\"value\"}"}'

# Base64 encode
curl -X POST https://toolpipe.dev/api/base64/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'

# CSV to JSON
curl -X POST https://toolpipe.dev/api/csv-to-json \
  -H "Content-Type: application/json" \
  -d '{"csv": "name,age\nAlice,30\nBob,25"}'

# Generate UUID
curl https://toolpipe.dev/api/uuid

# Lorem Ipsum
curl "https://toolpipe.dev/api/lorem?paragraphs=3"
```

## Code Tools APIs

```bash
# Code review
curl -X POST https://toolpipe.dev/api/code/review \
  -H "Content-Type: application/json" \
  -d '{"code": "function add(a, b) { return a + b; }", "language": "javascript"}'

# JSON to TypeScript
curl -X POST https://toolpipe.dev/api/json-to-typescript \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"name\": \"test\", \"count\": 42}"}'

# SQL formatter
curl -X POST https://toolpipe.dev/api/sql/format \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users WHERE age > 21 ORDER BY name"}'
```

## Security & Network APIs

```bash
# DNS lookup
curl "https://toolpipe.dev/api/dns/lookup?domain=github.com"

# SSL certificate check
curl "https://toolpipe.dev/api/ssl/check?domain=github.com"

# WHOIS lookup
curl "https://toolpipe.dev/api/whois?domain=example.com"

# Generate hash
curl -X POST https://toolpipe.dev/api/hash \
  -H "Content-Type: application/json" \
  -d '{"text": "hello", "algorithm": "sha256"}'

# JWT decode
curl -X POST https://toolpipe.dev/api/jwt/decode \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGciOiJIUzI1NiJ9..."}'
```

## DevOps APIs

```bash
# Generate Dockerfile
curl -X POST https://toolpipe.dev/api/dockerfile \
  -H "Content-Type: application/json" \
  -d '{"language": "node", "version": "20"}'

# Generate Docker Compose
curl -X POST https://toolpipe.dev/api/docker-compose \
  -H "Content-Type: application/json" \
  -d '{"services": ["node", "postgres", "redis"]}'

# Parse cron expression
curl "https://toolpipe.dev/api/cron/parse?expression=0+9+*+*+1-5"
```

## Web Tool APIs

```bash
# Generate QR code
curl "https://toolpipe.dev/api/qr?text=https://example.com&size=300"

# Shorten URL
curl -X POST https://toolpipe.dev/api/url/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://very-long-url.com/path/to/something"}'

# HTTP headers check
curl "https://toolpipe.dev/api/headers?url=https://github.com"

# Extract web content
curl -X POST https://toolpipe.dev/api/web/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Full API Docs

All 220+ endpoints are documented at [toolpipe.dev/docs](https://toolpipe.dev/docs) with interactive examples.

## MCP Server for AI Assistants

These tools also work as an MCP server for Claude, Cursor, and Windsurf:

```bash
npx @cosai-labs/toolpipe-mcp-server
```

## Links

- [toolpipe.dev](https://toolpipe.dev) - Try all tools in the browser
- [API Documentation](https://toolpipe.dev/docs) - Full REST API reference
- [GitHub](https://github.com/COSAI-Labs/toolpipe) - Source code

Everything is free, no API key needed. What would you add to this list?
