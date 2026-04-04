---
title: "Free UUID Generator API: v4, v5, and v7"
tags: uuid,api,database,webdev
canonical_url: https://toolpipe.dev
published: false
---

Generate UUIDs via API. Supports v4 (random), v5 (deterministic), and v7 (time-ordered).

## Quick Examples

```bash
# Single v4 UUID
curl "https://toolpipe.dev/uuid/generate?version=4"

# 10 v7 UUIDs (time-ordered, great for database PKs)
curl "https://toolpipe.dev/uuid/generate?version=7&count=10"

# v5 UUID (deterministic from namespace + name)
curl "https://toolpipe.dev/uuid/generate?version=5&namespace=6ba7b810-9dad-11d1-80b4-00c04fd430c8&name=example.com"
```

## Why v7?

UUID v7 includes a timestamp prefix, making them naturally sortable. This is ideal for database primary keys where insert order matters for index performance.

## Bulk Generation

Generate up to 1000 UUIDs per request. Perfect for seeding test databases or generating batch identifiers.

Free at [toolpipe.dev](https://toolpipe.dev). 120+ developer tools available.
