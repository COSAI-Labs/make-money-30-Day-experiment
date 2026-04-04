---
title: "Free GitHub Actions Workflow Generator API: CI/CD Templates via REST"
published: false
tags: ["api", "github", "cicd", "devops"]
---

Generate CI/CD workflow YAML with a single API call.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/github-actions/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "node-ci", "nodeVersion": "20"}'
```

## Workflow Types

- CI (test, lint, build)
- CD (deploy to Vercel, AWS, GCP)
- Docker build and push
- Release automation
- Scheduled tasks

Supports Node.js, Python, Go, Java, Rust. Custom matrix builds.

Free at [toolpipe.dev](https://toolpipe.dev/docs) - no signup required.
