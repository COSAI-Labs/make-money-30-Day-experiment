---
title: "Generate Docker Compose Files with a Free API"
tags: ["docker", "devops", "api", "automation"]
series: "Free Developer Tools"
published: false
---

ToolPipe can generate Docker Compose YAML files from a simple API call. Perfect for scaffolding new projects or automating infrastructure setup.

## API Endpoint

```bash
curl -X POST https://toolpipe.dev/api/docker-compose/generate \
  -H "Content-Type: application/json" \
  -d '{"services": ["nginx", "postgres", "redis"]}'
```

Returns a complete docker-compose.yml with proper networking, volumes, and environment variables.

## Also Available

- Nginx config generation
- GitHub Actions workflow generation  
- Kubernetes manifest helpers
- 115+ more free developer tools

All at [toolpipe.dev](https://toolpipe.dev). MCP server: `npx @cosai-labs/toolpipe-mcp-server`
