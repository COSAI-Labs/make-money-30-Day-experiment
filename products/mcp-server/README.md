# toolpipe-mcp-server

MCP server for [ToolPipe](https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server): 70+ developer utility APIs accessible to AI agents via the Model Context Protocol.

## Quick Start

### Install from GitHub Packages

```bash
npm install @cosai-labs/toolpipe-mcp-server
```

### Or run directly from the repo

```bash
git clone https://github.com/COSAI-Labs/make-money-30day-challenge.git
cd make-money-30day-challenge/products/mcp-server
npm install
node index.js
```

## Configuration

### Claude Desktop / Claude Code

Add to your config (`~/.claude/settings.json` or Claude Desktop settings):

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "node",
      "args": ["/path/to/products/mcp-server/index.js"],
      "env": {
        "TOOLPIPE_API_KEY": "tp_your_key_here",
        "TOOLPIPE_BASE_URL": "https://toolpipe.dev"
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
      "command": "node",
      "args": ["/path/to/products/mcp-server/index.js"],
      "env": {
        "TOOLPIPE_BASE_URL": "https://toolpipe.dev"
      }
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOOLPIPE_API_KEY` | (none) | API key for authenticated access |
| `TOOLPIPE_BASE_URL` | `https://toolpipe.dev` | API base URL |

## Available Tools (34)

### Data & Formatting
| Tool | Description |
|------|-------------|
| `json_format` | Format, validate, pretty-print JSON |
| `json_to_yaml` | Convert JSON to YAML |
| `json_to_csv` | Convert JSON to CSV |
| `json_validate_schema` | Validate JSON against JSON Schema |
| `code_format` | Format code (JSON, SQL, HTML) |
| `markdown_to_html` | Convert Markdown to HTML |
| `markdown_table` | Generate markdown tables from data |
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
| `regex_test` | Test regex patterns with full match details |

### Encoding & Hashing
| Tool | Description |
|------|-------------|
| `hash_text` | Hash text (MD5, SHA-1, SHA-256, SHA-512) |
| `base64_encode_decode` | Encode/decode Base64 |
| `url_encode_decode` | URL encode/decode |
| `jwt_decode` | Decode JWT tokens (header, payload, expiry) |
| `generate_uuid` | Generate UUIDs (v4) |
| `generate_password` | Generate secure random passwords |

### Web & Network
| Tool | Description |
|------|-------------|
| `dns_lookup` | DNS lookup (A, AAAA, MX, NS, TXT) |
| `ip_lookup` | IP geolocation lookup |
| `extract_metadata` | Extract URL metadata (OG, Twitter cards) |
| `check_website_status` | Check if website is up/down |
| `seo_analyze` | SEO analysis of any URL |
| `http_request` | Make HTTP requests (like curl via API) |
| `shorten_url` | Create shortened URLs |

### Utilities
| Tool | Description |
|------|-------------|
| `generate_qr_code` | Generate QR code image URLs |
| `color_convert` | Convert between HEX, RGB, HSL |
| `timestamp_convert` | Convert timestamps and dates |
| `cron_parse` | Parse cron expressions to plain English |
| `get_crypto_prices` | Live crypto prices (BTC, ETH, SOL) |
| `get_random_quote` | Random quotes |

## Pricing

- **Free**: 100 requests/day (no API key needed for basic use)
- **Pro**: $9.99/mo, 10,000 requests/day
- **Enterprise**: $49.99/mo, 100,000 requests/day

Pay with crypto (BTC, ETH, USDT, SOL, and 20+ more). No KYC needed.

## License

MIT
