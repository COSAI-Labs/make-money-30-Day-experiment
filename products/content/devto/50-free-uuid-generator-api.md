---
title: "Free UUID Generator API: v4 and Batch Generation via REST"
published: false
tags: uuid, api, webdev, tutorial
---

Need to generate UUIDs in your app without importing a library? Here's a free API that does it.

## Generate a UUID

```bash
curl https://toolpipe.dev/uuid/generate
```

Returns: `{ "uuid": "550e8400-e29b-41d4-a716-446655440000" }`

## Batch Generation

```bash
curl https://toolpipe.dev/uuid/generate?count=10
```

No signup, no API key for the free tier (100 calls/day).

Part of [ToolPipe](https://toolpipe.dev) - 120+ free developer APIs.
