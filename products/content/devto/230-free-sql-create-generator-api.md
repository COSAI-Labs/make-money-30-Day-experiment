---
title: "Free SQL CREATE TABLE Generator API"
published: false
tags: sql, api, database, webdev
canonical_url: https://toolpipe.dev/api
---

Generate SQL CREATE TABLE statements from JSON schema definitions with ToolPipe's free API.

## Usage

```bash
curl -X POST https://toolpipe.dev/api/generate/sql-create \
  -H "Content-Type: application/json" \
  -d '{"table": "users", "columns": [{"name": "id", "type": "int", "primary": true}]}'
```

No signup, no API key. **70+ free tools at [toolpipe.dev/api](https://toolpipe.dev/api)**
