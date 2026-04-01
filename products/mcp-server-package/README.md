# @toolpipe/mcp-server

MCP (Model Context Protocol) server for [ToolPipe](https://toolpipe.dev) -- 35 developer utility APIs accessible to AI agents.

## Tools Included

| # | Tool | Description |
|---|------|-------------|
| 1 | `json_format` | Format, validate, pretty-print JSON |
| 2 | `generate_qr_code` | Generate QR code image URLs |
| 3 | `generate_hash` | MD5, SHA-1, SHA-256, SHA-512 hashing |
| 4 | `generate_uuid` | Generate UUIDs (v4) |
| 5 | `base64` | Encode/decode Base64 strings |
| 6 | `markdown_to_html` | Convert Markdown to HTML |
| 7 | `shorten_url` | Shorten long URLs |
| 8 | `regex_test` | Test regex patterns against text |
| 9 | `text_stats` | Word count, reading time, etc. |
| 10 | `jwt_decode` | Decode JWT tokens |
| 11 | `dns_lookup` | DNS record lookups (A, MX, TXT, etc.) |
| 12 | `http_headers` | Check HTTP response headers |
| 13 | `ssl_check` | Inspect SSL/TLS certificates |
| 14 | `generate_password` | Generate strong random passwords |
| 15 | `lorem_ipsum` | Generate placeholder text |
| 16 | `convert_color` | Convert between HEX, RGB, HSL |
| 17 | `parse_cron` | Parse cron expressions to human-readable text |
| 18 | `convert_timestamp` | Convert Unix timestamps and ISO dates |
| 19 | `csv_to_json` | Convert CSV data to JSON |
| 20 | `minify_code` | Minify JavaScript, CSS, or HTML |
| 21 | `code_review` | Review code for bugs, security, best practices |
| 22 | `code_explain` | Explain code in plain English |
| 23 | `code_format` | Format/beautify code in many languages |
| 24 | `generate_fake_data` | Generate realistic mock data (names, emails, etc.) |
| 25 | `json_schema_validate` | Validate JSON against a JSON Schema |
| 26 | `whois_lookup` | WHOIS domain registration info |
| 27 | `generate_dockerfile` | Generate Dockerfiles for any language/framework |
| 28 | `generate_docker_compose` | Generate docker-compose.yml for multi-service stacks |
| 29 | `generate_commit_message` | Generate conventional git commit messages |
| 30 | `generate_regex` | Generate regex from natural language |
| 31 | `sql_format` | Format and beautify SQL queries |
| 32 | `json_to_typescript` | Generate TypeScript interfaces from JSON |
| 33 | `jwt_create` | Create signed JWT tokens |
| 34 | `web_extract` | Extract structured content from URLs |
| 35 | `prompt_engineer` | Improve and optimize LLM prompts |

## Installation

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["-y", "@toolpipe/mcp-server"],
      "env": {
        "TOOLPIPE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add toolpipe -- npx -y @toolpipe/mcp-server
```

### Cursor / Windsurf / Other MCP Clients

```json
{
  "toolpipe": {
    "command": "npx",
    "args": ["-y", "@toolpipe/mcp-server"]
  }
}
```

### Direct Usage

```bash
npx @toolpipe/mcp-server
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TOOLPIPE_BASE_URL` | API base URL | `https://toolpipe.dev` |
| `TOOLPIPE_API_KEY` | API key for higher rate limits | (none, free tier) |

## Pricing

- **Free**: 100 API calls per day, no signup required
- **Pro**: 10,000 API calls per day for $9.99/month
- **Enterprise**: 100,000 API calls per day for $49.99/month

Pay with crypto (BTC, ETH, USDT, SOL). No KYC required.

Get an API key at [https://toolpipe.dev](https://toolpipe.dev).

## Why ToolPipe?

- **35 tools in one package**: No need to install multiple MCP servers
- **Works out of the box**: No API key needed for free tier
- **AI-agent friendly**: Designed for Claude, GPT, and other LLM agents
- **Fast**: Sub-100ms response times for most tools
- **Reliable**: 99.9% uptime, rate-limited to prevent abuse

## Requirements

- Node.js 18 or later

## License

MIT
