---
title: "Free JSON to YAML Converter API for DevOps Workflows"
published: false
tags: ["api", "devops", "yaml", "tools"]
---

Convert JSON to YAML and back with ToolPipe's free converter API. Essential for Kubernetes configs, Docker Compose files, and CI/CD pipelines.

## API Endpoint

```
POST https://toolpipe.dev/api/convert/json-to-yaml
Content-Type: application/json

{"json": {"name": "app", "version": "1.0", "replicas": 3}}

Response:
name: app
version: "1.0"
replicas: 3
```

Use cases: Kubernetes manifests, Helm charts, GitHub Actions workflows, Docker Compose configs.

70+ free developer APIs at [toolpipe.dev](https://toolpipe.dev). Docs: [toolpipe.dev/docs](https://toolpipe.dev/docs)
