---
title: "Free Slug Generator API for SEO-Friendly URLs"
tags: seo,api,urls,webdev
canonical_url: https://toolpipe.dev
published: false
---

Transform any text into URL-safe slugs with the free ToolPipe API.

## Example

```bash
curl -X POST https://toolpipe.dev/text/slugify \
  -H "Content-Type: application/json" \
  -d '{"text": "My Awesome Blog Post! (Part 2)"}'

# Returns: my-awesome-blog-post-part-2
```

## Features

- Unicode transliteration ("Uber" from "Über")
- Custom separators (dash, underscore, dot)
- Max length control
- Special character removal
- Lowercase normalization

## Use Cases

- CMS URL generation
- File naming from user input
- SEO-friendly permalink creation
- Database-safe identifiers

Free at [toolpipe.dev](https://toolpipe.dev). No signup needed.
