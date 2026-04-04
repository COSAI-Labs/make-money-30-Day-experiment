---
title: "Free Slug Generator API: URL-Friendly Strings with Unicode Support"
published: false
tags: api, slug, webdev, seo
---

Generate clean URL slugs from any text, with Unicode transliteration and custom separators.

```bash
curl -X POST https://toolpipe.dev/api/slug/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World! This is a Test 🎉"}'
# Returns: {"slug": "hello-world-this-is-a-test"}
```

Perfect for CMS systems, blog engines, and SEO-friendly URLs. [API docs](https://toolpipe.dev/docs)
