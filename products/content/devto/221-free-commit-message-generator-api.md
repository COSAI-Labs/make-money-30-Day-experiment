---
title: "Free Commit Message Generator API"
published: false
tags: ["git", "api", "productivity", "webdev"]
---

## Free Commit Message Generator API

Generate conventional commit messages from code diffs via API.

### Endpoint

```
POST https://toolpipe.dev/api/commit/message
```

### Example

```bash
curl -X POST https://toolpipe.dev/api/commit/message \
  -H "Content-Type: application/json" \
  -d '{"diff": "added email validation to signup form, fixed password strength meter"}'
```

### Features

- Conventional Commits format
- Automatic type detection (feat, fix, refactor, etc.)
- Scope detection
- Breaking change detection

No signup required. Part of 240+ free tools at [toolpipe.dev](https://toolpipe.dev).
