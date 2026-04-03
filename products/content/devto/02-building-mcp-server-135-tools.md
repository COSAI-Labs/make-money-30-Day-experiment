---
title: "Building an MCP Server with 135+ Tools for AI Agents"
published: false
description: "How we built an MCP server that gives AI agents like Claude access to 135+ developer tools. Architecture, implementation, and use cases."
tags: ai, mcp, llm, devtools
canonical_url: https://toolpipe.dev
---

# Building an MCP Server with 135+ Tools for AI Agents

The Model Context Protocol (MCP) is changing how AI agents interact with the outside world. Instead of training models on everything, you give them access to tools they can call when needed.

We built [ToolPipe](https://toolpipe.dev), an MCP server that exposes 135+ developer tools to any MCP-compatible AI agent. Here is how it works and why it matters.

## What is MCP?

MCP (Model Context Protocol) is an open standard for connecting AI assistants to external tools and data sources. Think of it as a USB-C port for AI: a universal interface that any AI agent can plug into to gain new capabilities.

When an AI agent connects to an MCP server, it gets:
- A list of available tools with descriptions
- The ability to call those tools with structured parameters
- Typed responses it can reason about

## Why 135+ Tools in One Server?

Most MCP servers do one thing: search the web, query a database, or manage files. We took a different approach: give agents access to an entire toolkit of developer utilities.

When an AI agent is helping a developer, it might need to:
- Format JSON to check its structure
- Generate a UUID for a new database record
- Look up DNS records to debug a networking issue
- Decode a JWT to inspect its claims
- Generate a QR code for a URL
- Check SSL certificate expiry dates

With ToolPipe, the agent has all of these capabilities without needing separate MCP servers for each.

## Architecture

The server is structured around tool categories:

```
toolpipe-mcp/
  tools/
    text/         # JSON, Base64, URL encode/decode, Markdown
    crypto/       # Hash, UUID, JWT, password tools
    network/      # DNS, WHOIS, SSL, HTTP headers
    code/         # Regex, color convert, code review
    media/        # QR code, image placeholder
    time/         # Timestamp, timezone conversion
    docker/       # Dockerfile analysis, compose tools
```

Each tool is registered with:
- A unique name (e.g., `json_format`, `dns_lookup`)
- A description that helps the AI decide when to use it
- An input schema (JSON Schema) defining the parameters
- A handler function that executes the tool

## Installation

### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["toolpipe-mcp"]
    }
  }
}
```

### For Claude Code

```bash
claude mcp add toolpipe -- npx toolpipe-mcp
```

### For Any MCP Client

The server speaks standard MCP over stdio, so any MCP-compatible client can connect:

```bash
npx toolpipe-mcp
```

## Use Cases

### 1. Development Workflow Automation

An AI coding assistant can use ToolPipe to:
- Validate JSON configurations while editing
- Generate UUIDs for test fixtures
- Check regex patterns before applying them
- Convert timestamps in log analysis

### 2. DevOps and Infrastructure

Agents working on infrastructure can:
- Run DNS lookups to verify deployments
- Check SSL certificates before they expire
- Analyze Dockerfiles for best practices
- Inspect HTTP headers for security issues

### 3. Security Auditing

Security-focused agents can:
- Decode JWTs to inspect token claims
- Check password strength in configuration reviews
- Verify SSL/TLS configurations
- Perform WHOIS lookups on suspicious domains

### 4. Content Generation

Agents creating content can:
- Generate QR codes for documentation
- Convert Markdown to HTML for previews
- Create placeholder images for mockups

## Example: Agent Debugging a DNS Issue

Here is what happens when an agent uses ToolPipe to help debug a DNS issue:

**User**: "My site example.com isn't loading. Can you check what's going on?"

**Agent** (internally calls `dns_lookup` tool):
```json
{
  "tool": "dns_lookup",
  "params": {
    "domain": "example.com",
    "type": "A"
  }
}
```

**Agent** (then calls `ssl_check` tool):
```json
{
  "tool": "ssl_check",
  "params": {
    "domain": "example.com"
  }
}
```

**Agent** (then calls `http_headers` tool):
```json
{
  "tool": "http_headers",
  "params": {
    "url": "https://example.com"
  }
}
```

The agent can now provide a comprehensive diagnosis covering DNS resolution, SSL status, and HTTP response headers, all without the developer leaving their editor.

## Performance

All tools return results in under 200ms for local operations (JSON formatting, hashing, UUID generation). Network tools (DNS, WHOIS, SSL) depend on external resolution but typically complete in under 2 seconds.

The server starts in under 1 second and has no persistent state or database requirements.

## Open Source

ToolPipe is fully open source: [github.com/COSAI-Labs/toolpipe](https://github.com/COSAI-Labs/toolpipe)

The web UI at [toolpipe.dev](https://toolpipe.dev) provides the same 220+ tools with a browser interface, and the REST API is available for direct integration without MCP.

## What's Next

We are actively adding new tools based on community requests. Current priorities:
- GraphQL schema validation
- OpenAPI spec linting
- Git diff formatting
- CSV/JSON conversion tools
- More Docker and Kubernetes utilities

If you have a tool you'd like to see, open an issue on GitHub or drop a comment below.

---

Have you built or used an MCP server? What tools would be most useful for your AI agent workflows?
