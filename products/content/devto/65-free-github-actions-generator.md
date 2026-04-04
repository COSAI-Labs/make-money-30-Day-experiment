---
title: "Free GitHub Actions Generator API: Create CI/CD Workflows via REST"
published: false
tags: github, cicd, api, devops
---

Generate GitHub Actions workflow YAML files programmatically.

```bash
curl -X POST https://toolpipe.dev/github-actions/generate \
  -H "Content-Type: application/json" \
  -d '{"name": "CI", "trigger": "push", "steps": ["checkout", "setup-node", "install", "test"]}'
```

Free, no signup. [Full docs](https://toolpipe.dev/docs) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
