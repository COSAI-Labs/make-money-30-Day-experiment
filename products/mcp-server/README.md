# ToolPipe MCP Server

95+ developer utility tools for AI agents via [Model Context Protocol](https://modelcontextprotocol.io). JSON formatting, QR codes, hashing, UUID, DNS, regex, JWT, SQL formatting, XML/YAML conversion, webhook testing, mock data generation, crontab generation, web scraping, code analysis, and more.

Works with Claude, Cursor, Windsurf, VS Code, or any MCP-compatible client.

## Quick Start

### Remote (Zero Install, Recommended)

Connect directly to the hosted server:

**Claude Desktop / Claude Code:**
```json
{
  "mcpServers": {
    "toolpipe": {
      "url": "https://toolpipe.dev/mcp"
    }
  }
}
```

### Local (via npx)

```bash
npx @cosai-labs/toolpipe-mcp-server
```

**Claude Desktop (local):**
```json
{
  "mcpServers": {
    "toolpipe": {
      "command": "npx",
      "args": ["-y", "@cosai-labs/toolpipe-mcp-server"],
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
      "url": "https://toolpipe.dev/mcp"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOOLPIPE_API_KEY` | (none) | API key for higher rate limits |
| `TOOLPIPE_BASE_URL` | `https://toolpipe.dev` | API base URL |
| `TOOLPIPE_LOCAL` | `false` | Use local implementations for basic tools |

Get a free API key (100 calls/day): `POST /api-keys/register` with `{"email": "you@example.com"}`. No signup beyond email.

## 95+ Tools

### Data and Formatting
| Tool | Description |
|------|-------------|
| `json_format` | Format, validate, pretty-print JSON (local) |
| `json_to_yaml` | Convert JSON to YAML |
| `json_to_csv` | Convert JSON array to CSV |
| `json_validate_schema` | Validate JSON against JSON Schema |
| `json_query` | Query JSON with dot-notation paths |
| `json_to_schema` | Generate JSON Schema from example data |
| `json_diff` | Compare two JSON objects |
| `code_format` | Format code (JSON, SQL, HTML) |
| `csv_to_json` | Convert CSV to JSON |
| `yaml_to_json` | Convert YAML to JSON |
| `xml_to_json` | Convert XML to JSON |
| `yaml_validate` | Validate YAML, convert to JSON |
| `env_parse` | Parse .env files to JSON |

### Text Processing
| Tool | Description |
|------|-------------|
| `analyze_text` | Word count, reading time, sentence count |
| `text_stats` | Text statistics and readability scores |
| `summarize_text` | Extractive text summarization |
| `detect_language` | Language detection |
| `text_diff` | Compare two texts (unified diff) |
| `text_similarity` | Jaccard, cosine, character similarity |
| `slugify` | Convert text to URL-friendly slugs |
| `slug_generate` | Generate URL slugs |
| `regex_test` | Test regex patterns with match details |
| `lorem_ipsum` | Generate placeholder text |
| `markdown_to_html` | Convert Markdown to HTML |
| `markdown_table` | Generate markdown tables |
| `markdown_strip` | Strip markdown to plain text |
| `html_strip` | Strip HTML tags to plain text |
| `sql_format` | Format SQL queries |

### Encoding and Security
| Tool | Description |
|------|-------------|
| `hash_text` | Hash text: MD5, SHA-1, SHA-256, SHA-512 (local) |
| `base64_encode_decode` | Encode/decode Base64 (local) |
| `url_encode_decode` | URL encode/decode |
| `html_encode_decode` | HTML entity encode/decode |
| `jwt_decode` | Decode JWT tokens |
| `jwt_create` | Create JWT tokens for testing |
| `generate_uuid` | Generate UUIDs v4 (local) |
| `generate_password` | Generate secure passwords |
| `password_check` | Check password strength and crack time |
| `number_convert` | Convert decimal/binary/hex/roman |
| `number_format` | Format numbers: comma, words, scientific |

### Web and Network
| Tool | Description |
|------|-------------|
| `dns_lookup` | DNS lookup (A, AAAA, MX, NS, TXT) |
| `ip_lookup` | IP geolocation |
| `validate_ip` | Validate and classify IP addresses |
| `validate_email` | Validate email format and MX records |
| `extract_metadata` | Extract URL metadata (OG tags) |
| `check_website_status` | Check if website is up/down |
| `seo_analyze` | SEO analysis |
| `http_request` | HTTP requests (curl via API) |
| `headers_analyze` | Analyze HTTP response headers |
| `web_extract` | Extract content from web pages |
| `shorten_url` | Create shortened URLs |
| `http_status` | HTTP status code reference |
| `my_ip` | Get caller's IP address |
| `test_endpoint` | Test API endpoints with timing |

### Code and DevOps
| Tool | Description |
|------|-------------|
| `code_analyze` | Analyze code: language, functions, complexity |
| `schema_generate` | Generate TypeScript/Python/Zod schemas |
| `generate_gitignore` | Generate .gitignore for any language |
| `generate_dockerfile` | Generate Dockerfiles |
| `generate_env_file` | Generate env files |
| `generate_openapi` | Generate OpenAPI specs |

### Media and Visual
| Tool | Description |
|------|-------------|
| `generate_qr_code` | Generate QR code URLs |
| `color_convert` | Convert HEX/RGB/HSL colors |
| `color_palette` | Generate color palettes |

### Utilities
| Tool | Description |
|------|-------------|
| `timestamp_convert` | Convert timestamps/dates |
| `cron_parse` | Parse cron to plain English |
| `get_crypto_prices` | Live crypto prices |
| `css_minify` | Minify CSS |
| `js_minify` | Minify JavaScript |
| `get_random_quote` | Random quotes |
| `generate_fake_data` | Generate mock data |
| `template_render` | Render templates with variables |
| `data_transform` | Sort, filter, group JSON data |
| `prompt_build` | Build structured LLM prompts |

### Testing and DevOps
| Tool | Description |
|------|-------------|
| `webhook_create` | Create a webhook bin for testing |
| `webhook_inspect` | Inspect captured webhook requests |
| `mock_generate` | Generate mock API data (user, product, order, comment, post) |
| `crontab_generate` | Generate cron expressions from plain English |
| `diff_generate` | Generate diff/patch between two texts |
| `api_stats` | Get ToolPipe API statistics |

### Account and Payments
| Tool | Description |
|------|-------------|
| `register_api_key` | Register a free API key |
| `check_api_usage` | Check API key usage and quota |
| `create_payment` | Create crypto payment order |
| `verify_payment` | Verify crypto payment on-chain |
| `get_pricing` | Get pricing tiers and payment info |

## Pricing

| Plan | Price | Daily Limit |
|------|-------|-------------|
| Free | $0 | 100 calls/day |
| Pro | $9.99/mo | 10,000 calls/day |
| Enterprise | $49.99/mo | 100,000 calls/day |

Pay with crypto (ETH, USDC, USDT, DAI). No KYC needed. AI agents can pay programmatically.

## API

The underlying REST API has 130+ endpoints. Interactive docs at `/docs`. Quick start guide at `/quickstart`.

## License

MIT
