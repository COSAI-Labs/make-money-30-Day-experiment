# toolpipe-mcp-server

MCP server providing 80+ developer utility APIs to AI agents via the [Model Context Protocol](https://modelcontextprotocol.io). Use it with Claude, Cursor, VS Code, Windsurf, or any MCP-compatible client.

## Quick Start

### Remote (Zero Install)

Connect directly to the hosted server. No npm install needed:

**Claude Desktop / Claude Code:**
```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://assessing-scoop-authorities-sheet.trycloudflare.com/mcp"
    }
  }
}
```

### Local (npm)

```bash
npx toolpipe-mcp-server
```

Or install globally:
```bash
npm install -g toolpipe-mcp-server
toolpipe-mcp
```

### Claude Desktop (local)

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["-y", "toolpipe-mcp-server"],
      "env": {
        "TOOLPIPE_API_KEY": "tp_your_key_here"
      }
    }
  }
}
```

### Cursor / VS Code

Add to `.cursor/mcp.json` or `.vscode/mcp.json`:
```json
{
  "servers": {
    "toolpipe": {
      "command": "npx",
      "args": ["-y", "toolpipe-mcp-server"]
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOOLPIPE_API_KEY` | (none) | API key for higher rate limits |
| `TOOLPIPE_BASE_URL` | `https://toolpipe.dev` | API base URL |

Get a free API key (100 calls/day) at the `/api-keys` endpoint. No signup required beyond email.

## 34 Tools Available

### Data & Formatting
| Tool | Description |
|------|-------------|
| `json_format` | Format, validate, pretty-print JSON |
| `json_to_yaml` | Convert JSON to YAML |
| `json_to_csv` | Convert JSON array to CSV |
| `json_validate_schema` | Validate JSON against JSON Schema |
| `code_format` | Format/beautify code (JSON, SQL, HTML) |
| `markdown_to_html` | Convert Markdown to HTML |
| `markdown_table` | Generate markdown tables |
| `css_minify` | Minify CSS |
| `js_minify` | Minify JavaScript |

### Text Processing
| Tool | Description |
|------|-------------|
| `analyze_text` | Word count, reading time, sentence count |
| `summarize_text` | Extractive text summarization |
| `detect_language` | Language detection |
| `text_diff` | Compare two texts (unified diff) |
| `slugify` | Convert text to URL-friendly slugs |
| `regex_test` | Test regex patterns with match details |
| `lorem_ipsum` | Generate placeholder text |

### Encoding & Security
| Tool | Description |
|------|-------------|
| `hash_text` | Hash text (MD5, SHA-1, SHA-256, SHA-512) |
| `base64_encode_decode` | Encode/decode Base64 |
| `url_encode_decode` | URL encode/decode |
| `jwt_decode` | Decode JWT tokens |
| `generate_uuid` | Generate UUIDs (v4) |
| `generate_password` | Generate secure passwords |

### Web & Network
| Tool | Description |
|------|-------------|
| `dns_lookup` | DNS lookup (A, AAAA, MX, NS, TXT) |
| `ip_lookup` | IP geolocation |
| `extract_metadata` | Extract URL metadata (OG tags) |
| `check_website_status` | Check if website is up/down |
| `seo_analyze` | SEO analysis |
| `http_request` | HTTP requests (curl via API) |
| `shorten_url` | Create shortened URLs |

### Utilities
| Tool | Description |
|------|-------------|
| `generate_qr_code` | Generate QR code URLs |
| `color_convert` | Convert HEX/RGB/HSL colors |
| `timestamp_convert` | Convert timestamps/dates |
| `cron_parse` | Parse cron to plain English |
| `get_crypto_prices` | Live crypto prices |
| `get_random_quote` | Random quotes |

## Pricing

| Plan | Price | Daily Limit |
|------|-------|-------------|
| Free | $0/mo | 100 requests/day |
| Pro | $9.99/mo | 10,000 requests/day |
| Enterprise | $49.99/mo | 100,000 requests/day |

Pay with crypto (ETH, USDC, USDT, and more). No KYC needed.

## API

The underlying REST API has 80+ endpoints. Full OpenAPI docs at `/docs`.

## License

MIT
