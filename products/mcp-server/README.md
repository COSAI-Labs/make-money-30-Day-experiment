# @toolpipe/mcp-server

MCP server for [ToolPipe](https://toolpipe.dev): 70+ developer utility APIs accessible to AI agents via the Model Context Protocol.

## Quick Start

```bash
npx @toolpipe/mcp-server
```

## Configuration

Add to your Claude Desktop config (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["@toolpipe/mcp-server"],
      "env": {
        "TOOLPIPE_API_KEY": "tp_your_key_here"
      }
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOOLPIPE_API_KEY` | (none) | API key for authenticated access (get free key at /api-keys) |
| `TOOLPIPE_BASE_URL` | `https://toolpipe.dev` | Custom API base URL |

## Available Tools (22)

| Tool | Description |
|------|-------------|
| `json_format` | Format, validate, pretty-print JSON |
| `generate_qr_code` | Generate QR code image URLs |
| `generate_uuid` | Generate UUIDs (v4) |
| `hash_text` | Hash text (MD5, SHA-1, SHA-256, SHA-512) |
| `base64_encode_decode` | Encode/decode Base64 |
| `dns_lookup` | DNS lookup (A, AAAA, MX, NS, TXT) |
| `markdown_to_html` | Convert Markdown to HTML |
| `analyze_text` | Word count, reading time, etc. |
| `css_minify` | Minify CSS |
| `js_minify` | Minify JavaScript |
| `json_to_yaml` | Convert JSON to YAML |
| `json_to_csv` | Convert JSON to CSV |
| `color_convert` | Convert between HEX, RGB, HSL |
| `extract_metadata` | Extract URL metadata (OG, Twitter) |
| `ip_lookup` | IP geolocation lookup |
| `check_website_status` | Check if website is up/down |
| `shorten_url` | Create shortened URLs |
| `get_random_quote` | Random quotes |
| `summarize_text` | Extractive text summarization |
| `detect_language` | Language detection |
| `get_crypto_prices` | Crypto prices (BTC, ETH, SOL) |
| `seo_analyze` | SEO analysis |

## Pricing

- **Free**: 100 requests/day (no API key needed for basic use)
- **Pro**: $9.99/mo, 10,000 requests/day
- **Enterprise**: $49.99/mo, 100,000 requests/day

Pay with crypto (BTC, ETH, USDT, SOL, and 20+ more). No KYC needed.

## License

MIT
