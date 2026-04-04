---
title: "Free SQL Formatter API: Pretty Print SQL Queries via REST"
published: false
tags: sql, database, api, devtools
---

Format and pretty-print SQL queries for readability.

```bash
curl -X POST https://toolpipe.dev/sql/format \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users WHERE age > 18 ORDER BY name"}'
```

Supports MySQL, PostgreSQL, SQLite syntax. Free, no signup.

[API docs](https://toolpipe.dev/docs) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
