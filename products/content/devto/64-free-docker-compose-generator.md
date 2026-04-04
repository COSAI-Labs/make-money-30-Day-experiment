---
title: "Free Docker Compose Generator API: Create Configs Programmatically"
published: false
tags: docker, devops, api, automation
---

Generate Docker Compose YAML files from service descriptions.

```bash
curl -X POST https://toolpipe.dev/docker-compose/generate \
  -H "Content-Type: application/json" \
  -d '{"services": [{"name": "web", "image": "nginx"}, {"name": "db", "image": "postgres"}]}'
```

Free, no signup. Part of 120+ ToolPipe developer tools.

[API docs](https://toolpipe.dev/docs) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
