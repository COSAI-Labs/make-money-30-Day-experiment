# @toolpipe/mcp-server

MCP (Model Context Protocol) server for [ToolPipe](https://toolpipe.dev) -- 20 essential developer utility APIs accessible to AI agents.

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

Get an API key at [https://toolpipe.dev](https://toolpipe.dev).

## Requirements

- Node.js 18 or later

## License

MIT
