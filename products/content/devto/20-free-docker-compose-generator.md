---
title: "Generate Docker Compose Files with AI: ToolPipe MCP Server"
published: false
tags: docker, devops, ai, mcp
canonical_url: https://toolpipe.dev
---

Writing docker-compose.yml files from scratch is tedious. With ToolPipe's MCP server, your AI coding agent can generate production-ready Docker Compose configurations from a natural language description.

## How It Works

1. Install the MCP server:

```bash
npx @cosai-labs/toolpipe-mcp-server
```

2. Ask your AI agent: "Generate a Docker Compose file for a Next.js app with PostgreSQL, Redis, and Nginx"

3. Get a complete docker-compose.yml with proper networking, volumes, health checks, and environment variables.

## Supported Stacks

- Node.js + PostgreSQL + Redis
- Python/Django + MySQL + Celery
- Go + MongoDB + Elasticsearch
- Any custom combination

## Part of 238 Developer Tools

The Docker Compose generator is one of 238 tools in the ToolPipe MCP server, including:

- Nginx config generator
- GitHub Actions workflow generator
- API client generator (TypeScript)
- OpenAPI spec generator
- Code review, formatting, minification

## Setup

Add to your Claude/Cursor/Windsurf config:

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["-y", "@cosai-labs/toolpipe-mcp-server"]
    }
  }
}
```

- **npm**: [@cosai-labs/toolpipe-mcp-server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
- **API**: [toolpipe.dev](https://toolpipe.dev)
