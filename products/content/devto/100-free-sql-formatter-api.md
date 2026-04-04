---
title: "Free SQL Formatter API: Pretty Print Your Queries via REST"
published: false
tags: ["sql", "database", "api", "productivity"]
canonical_url: "https://toolpipe.dev"
---

# Free SQL Formatter API

Format messy SQL queries into readable, properly indented code via a REST API call.

```bash
curl -X POST https://toolpipe.dev/sql/format \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT u.name, o.total FROM users u JOIN orders o ON u.id=o.user_id WHERE o.total>100 ORDER BY o.total DESC"}'
```

Supports MySQL, PostgreSQL, SQLite, and T-SQL dialects. No signup needed.

**120+ free developer tools at** [toolpipe.dev](https://toolpipe.dev)
