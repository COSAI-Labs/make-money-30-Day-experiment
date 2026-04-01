---
title: "The Free API Every Developer Needs: 70+ Endpoints, Zero Auth"
published: false
description: "ToolPipe gives you 70+ REST API endpoints for common developer tasks. JSON formatting, hashing, QR codes, regex testing, color conversion, and more. Free, no auth, CORS enabled."
tags: api, webdev, programming, tutorial
canonical_url:
cover_image:
---

I got tired of juggling a dozen browser tabs for basic dev tasks. JSON formatting in one tab. Base64 decoding in another. A regex tester in a third. Each one with its own UI, its own quirks, and most of them plastered with ads.

So I built **ToolPipe**: a single FastAPI service with 70+ REST endpoints covering the tasks developers do every day. It is completely free, requires no authentication, and has CORS enabled so you can call it from anywhere.

**Base URL:** `https://assessing-scoop-authorities-sheet.trycloudflare.com`
**Swagger Docs:** `https://assessing-scoop-authorities-sheet.trycloudflare.com/docs`

This article walks through the API by category with real `curl` examples you can copy and run right now.

---

## Getting Started

Every endpoint follows REST conventions. POST endpoints accept JSON bodies. GET endpoints use query parameters. All responses are JSON (except image endpoints).

No API key. No OAuth. No signup. Just make the request.

```bash
# Health check
curl https://assessing-scoop-authorities-sheet.trycloudflare.com/api/health
```

Response:
```json
{
  "status": "ok",
  "tools": 58,
  "endpoints": 70
}
```

---

## Category 1: JSON Tools

These are probably the endpoints you will reach for most often.

### Format / Pretty-Print JSON

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"users\":[{\"id\":1,\"name\":\"Alice\"},{\"id\":2,\"name\":\"Bob\"}]}"}'
```

Response:
```json
{
  "formatted": "{\n  \"users\": [\n    {\n      \"id\": 1,\n      \"name\": \"Alice\"\n    },\n    {\n      \"id\": 2,\n      \"name\": \"Bob\"\n    }\n  ]\n}",
  "valid": true
}
```

### Validate JSON

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/validate \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"missing\": \"closing bracket\""}'
```

Response:
```json
{
  "valid": false,
  "error": "Expecting ',' delimiter: line 1 column 30 (char 29)"
}
```

### Validate Against JSON Schema

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/validate-schema \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "type": "object",
      "required": ["name", "email"],
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
      }
    },
    "data": {"name": "Alice"}
  }'
```

Response:
```json
{
  "valid": false,
  "errors": ["'email' is a required property"]
}
```

### JSONPath Query

Extract nested data without writing code.

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/query \
  -H "Content-Type: application/json" \
  -d '{
    "json": {
      "store": {
        "books": [
          {"title": "Dune", "price": 12.99},
          {"title": "Neuromancer", "price": 9.99}
        ]
      }
    },
    "path": "$.store.books[?(@.price<10)].title"
  }'
```

Response:
```json
{
  "results": ["Neuromancer"]
}
```

---

## Category 2: Encoding and Decoding

### Base64

```bash
# Encode
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/base64/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "secret-api-key:12345"}'
```

Response:
```json
{
  "encoded": "c2VjcmV0LWFwaS1rZXk6MTIzNDU="
}
```

```bash
# Decode
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/base64/decode \
  -H "Content-Type: application/json" \
  -d '{"text": "c2VjcmV0LWFwaS1rZXk6MTIzNDU="}'
```

### URL Encoding

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/url/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "name=John Doe&city=New York&q=hello world"}'
```

Response:
```json
{
  "encoded": "name%3DJohn+Doe%26city%3DNew+York%26q%3Dhello+world"
}
```

### HTML Entities

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/html/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "<div class=\"alert\">User input: 5 > 3 & 2 < 4</div>"}'
```

Response:
```json
{
  "encoded": "&lt;div class=&quot;alert&quot;&gt;User input: 5 &gt; 3 &amp; 2 &lt; 4&lt;/div&gt;"
}
```

### JWT Decoding

Inspect tokens without a verification secret.

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/jwt/decode \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"}'
```

Response:
```json
{
  "header": {"alg": "HS256", "typ": "JWT"},
  "payload": {"sub": "1234567890", "name": "John Doe", "iat": 1516239022},
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

---

## Category 3: Hashing and Cryptography

### Generate Hashes

Supports MD5, SHA-1, SHA-256, and SHA-512.

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "password123", "algorithm": "sha256"}'
```

Response:
```json
{
  "algorithm": "sha256",
  "hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
}
```

### Password Generator

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/password/generate?length=32&symbols=true&numbers=true&uppercase=true"
```

Response:
```json
{
  "password": "kX#9mR$vL2@pN7wQ!fH4jS&cT8yU*bE6",
  "length": 32,
  "strength": "very_strong"
}
```

---

## Category 4: Text Processing

### Regex Tester

Test patterns and get match details without spinning up a REPL.

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/regex/test \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "(\\d{4})-(\\d{2})-(\\d{2})",
    "text": "Today is 2026-04-01 and tomorrow is 2026-04-02",
    "flags": "g"
  }'
```

Response:
```json
{
  "matches": [
    {
      "match": "2026-04-01",
      "groups": ["2026", "04", "01"],
      "index": 9
    },
    {
      "match": "2026-04-02",
      "groups": ["2026", "04", "02"],
      "index": 37
    }
  ],
  "count": 2
}
```

### Diff Checker

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/diff/compare \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "function hello() {\n  return \"hello\";\n}",
    "text2": "function hello() {\n  return \"hello, world\";\n}"
  }'
```

### Case Converter

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/text/case-convert \
  -H "Content-Type: application/json" \
  -d '{"text": "user profile settings page", "case": "camelCase"}'
```

Response:
```json
{
  "result": "userProfileSettingsPage",
  "original": "user profile settings page",
  "case": "camelCase"
}
```

Supported cases: `camelCase`, `PascalCase`, `snake_case`, `kebab-case`, `SCREAMING_SNAKE_CASE`, `Title Case`.

### Slugify

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/text/slugify \
  -H "Content-Type: application/json" \
  -d '{"text": "How to Build a REST API in 2026 (Complete Guide)"}'
```

Response:
```json
{
  "slug": "how-to-build-a-rest-api-in-2026-complete-guide"
}
```

---

## Category 5: Web and Network

### DNS Lookup

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/dns/lookup?domain=dev.to&type=A"
```

### SSL Certificate Check

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/ssl/check?domain=github.com"
```

Response:
```json
{
  "domain": "github.com",
  "issuer": "DigiCert",
  "valid_from": "2025-03-15T00:00:00Z",
  "valid_to": "2026-03-15T23:59:59Z",
  "days_remaining": 349,
  "is_valid": true
}
```

### HTTP Header Inspector

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/http/headers?url=https://dev.to"
```

### Open Graph Tags

Debug link previews by extracting OG meta tags.

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/og-tags?url=https://dev.to"
```

Response:
```json
{
  "og:title": "DEV Community",
  "og:description": "A constructive and inclusive social network for software developers.",
  "og:image": "https://dev-to-uploads.s3.amazonaws.com/...",
  "og:url": "https://dev.to"
}
```

---

## Category 6: Color Tools

### Convert Colors

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/color/convert?color=%233498db&format=rgb"
```

Response:
```json
{
  "hex": "#3498db",
  "rgb": "rgb(52, 152, 219)",
  "hsl": "hsl(204, 70%, 53%)",
  "name": "Curious Blue"
}
```

### Contrast Ratio (WCAG)

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/color/contrast?fg=%23ffffff&bg=%23003366"
```

Response:
```json
{
  "ratio": 10.52,
  "aa_normal": "pass",
  "aa_large": "pass",
  "aaa_normal": "pass",
  "aaa_large": "pass"
}
```

### Palette Generator

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/color/palette?base=%23e74c3c&type=analogous"
```

---

## Category 7: Date and Time

### Cron Parser

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/cron/parse \
  -H "Content-Type: application/json" \
  -d '{"expression": "0 9 * * 1-5"}'
```

Response:
```json
{
  "description": "At 09:00, Monday through Friday",
  "next_runs": [
    "2026-04-02T09:00:00Z",
    "2026-04-03T09:00:00Z",
    "2026-04-06T09:00:00Z"
  ]
}
```

### Timestamp Converter

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/timestamp/convert?timestamp=1711929600"
```

Response:
```json
{
  "unix": 1711929600,
  "iso": "2024-04-01T00:00:00Z",
  "human": "Monday, April 1, 2024 12:00:00 AM UTC",
  "relative": "2 years ago"
}
```

---

## Category 8: Generators

### UUID

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/uuid/generate?count=3"
```

Response:
```json
{
  "uuids": [
    "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "550e8400-e29b-41d4-a716-446655440000"
  ]
}
```

### QR Code

Returns a PNG image.

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/qr/generate?text=https://dev.to&size=300" \
  --output qr-devto.png
```

### Lorem Ipsum

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/lorem-ipsum?paragraphs=2&format=text"
```

### Placeholder Images

```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/image/placeholder?width=800&height=400&text=Banner&bg=3498db&fg=ffffff" \
  --output banner.png
```

---

## Category 9: Data Format Conversion

### Markdown to HTML

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/markdown/to-html \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## Features\n\n- Fast\n- Free\n- **No auth**\n\n```python\nprint(\"hello\")\n```"}'
```

### YAML to JSON

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/yaml/to-json \
  -H "Content-Type: application/json" \
  -d '{"yaml": "apiVersion: v1\nkind: Service\nmetadata:\n  name: my-service\nspec:\n  ports:\n    - port: 80"}'
```

### CSV to JSON

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/csv/to-json \
  -H "Content-Type: application/json" \
  -d '{"csv": "endpoint,method,description\n/api/json/format,POST,Format JSON\n/api/uuid/generate,GET,Generate UUIDs"}'
```

### SQL Formatter

```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/sql/format \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT u.id, u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.active = true GROUP BY u.id, u.name HAVING COUNT(o.id) > 5 ORDER BY order_count DESC LIMIT 10"}'
```

---

## Using ToolPipe in Your Stack

### From JavaScript (frontend or Node.js)

CORS is enabled, so browser calls work directly.

```javascript
async function formatJSON(messy) {
  const res = await fetch(
    'https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/format',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ json: messy })
    }
  );
  return res.json();
}
```

### From Python

```python
import requests

def generate_uuid(count=1):
    r = requests.get(
        f"https://assessing-scoop-authorities-sheet.trycloudflare.com/api/uuid/generate",
        params={"count": count}
    )
    return r.json()["uuids"]
```

### As Shell Aliases

Add these to your `.bashrc` or `.zshrc`:

```bash
alias json-format='curl -s -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/format -H "Content-Type: application/json" -d'
alias uuid='curl -s https://assessing-scoop-authorities-sheet.trycloudflare.com/api/uuid/generate | jq -r ".uuids[0]"'
alias qr='f(){ curl -s "https://assessing-scoop-authorities-sheet.trycloudflare.com/api/qr/generate?text=$1" -o qr.png && open qr.png; }; f'
```

### In CI/CD Pipelines

```yaml
# GitHub Actions example
- name: Validate API response schema
  run: |
    curl -s -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api/json/validate-schema \
      -H "Content-Type: application/json" \
      -d "{\"schema\": $(cat schema.json), \"data\": $(curl -s $API_URL)}" \
      | jq -e '.valid == true'
```

---

## Why Not Just Use [existing tool]?

Fair question. Here is why ToolPipe is different:

1. **One URL, 70+ tools.** No more bookmarking 30 different sites.
2. **API-first.** Every tool works via REST, not just in a browser.
3. **No auth.** No API keys, no OAuth, no signup. Just call the endpoint.
4. **CORS enabled.** Call it from your frontend, your scripts, your CI, your LLM agents.
5. **Fast.** Built on FastAPI (Python), responses are typically under 50ms.
6. **No ads, no tracking.** Just tools.

---

## Full Documentation

The complete Swagger/OpenAPI docs are interactive. You can test every endpoint in your browser:

[https://assessing-scoop-authorities-sheet.trycloudflare.com/docs](https://assessing-scoop-authorities-sheet.trycloudflare.com/docs)

---

## What's Next

More endpoints are being added regularly. If you have a tool you'd use daily, drop a comment. The ones most requested get built first.

Bookmark the base URL:
[https://assessing-scoop-authorities-sheet.trycloudflare.com](https://assessing-scoop-authorities-sheet.trycloudflare.com)
