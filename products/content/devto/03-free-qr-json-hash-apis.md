---
title: "Free QR Code, JSON, and Hash APIs for Developers"
published: false
description: "Three of the most commonly needed developer APIs, completely free with no signup. QR code generation, JSON formatting, and cryptographic hashing via simple REST endpoints."
tags: api, webdev, tutorial, beginners
canonical_url: https://toolpipe.dev
---

# Free QR Code, JSON, and Hash APIs for Developers

Three tools every developer needs at some point: QR code generation, JSON formatting, and cryptographic hashing. Here are free REST APIs for all three, with no signup, no API key, and no rate limits worth worrying about.

All examples use [ToolPipe](https://toolpipe.dev), which provides 220+ free developer tools as REST APIs.

## 1. QR Code Generation API

### Generate a Basic QR Code

```bash
curl -X POST https://toolpipe.dev/api/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "https://github.com"}' \
  -o qr-code.png
```

### With Custom Size

```bash
curl -X POST https://toolpipe.dev/api/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "https://toolpipe.dev", "size": 500}'
```

### Use Cases

- **Documentation**: Generate QR codes linking to API docs or demo pages
- **Event apps**: Create QR codes for ticket verification
- **Packaging**: Generate product QR codes in your build pipeline
- **Testing**: Quick QR codes for mobile app testing

### Python Example

```python
import requests

response = requests.post(
    "https://toolpipe.dev/api/qr/generate",
    json={"text": "https://my-app.com/download", "size": 400}
)

with open("download-qr.png", "wb") as f:
    f.write(response.content)
```

### JavaScript/Node.js Example

```javascript
const response = await fetch("https://toolpipe.dev/api/qr/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "https://my-app.com/download",
    size: 400
  })
});

const blob = await response.blob();
// Use the blob in your app
```

## 2. JSON Formatting API

### Format Messy JSON

```bash
curl -X POST https://toolpipe.dev/api/json/format \
  -H "Content-Type: application/json" \
  -d '{"json_string": "{\"users\":[{\"id\":1,\"name\":\"Alice\"},{\"id\":2,\"name\":\"Bob\"}]}"}'
```

Response:
```json
{
  "formatted": "{\n  \"users\": [\n    {\n      \"id\": 1,\n      \"name\": \"Alice\"\n    },\n    {\n      \"id\": 2,\n      \"name\": \"Bob\"\n    }\n  ]\n}"
}
```

### Validate JSON

```bash
curl -X POST https://toolpipe.dev/api/json/validate \
  -H "Content-Type: application/json" \
  -d '{"json_string": "{\"key\": \"value\",}"}'
```

This returns validation errors, pointing to the exact location of syntax issues.

### Use Cases

- **CI/CD pipelines**: Validate JSON config files before deployment
- **Log analysis**: Format single-line JSON logs for readability
- **API development**: Pretty-print API responses during debugging
- **Code review**: Format JSON fixtures in test files

### Shell Script: Format All JSON Files

```bash
#!/bin/bash
for file in *.json; do
  content=$(cat "$file")
  curl -s -X POST https://toolpipe.dev/api/json/format \
    -H "Content-Type: application/json" \
    -d "{\"json_string\": $(echo "$content" | jq -Rs .)}" \
    | jq -r '.formatted' > "$file.tmp"
  mv "$file.tmp" "$file"
  echo "Formatted: $file"
done
```

## 3. Cryptographic Hash API

### Generate a SHA-256 Hash

```bash
curl -X POST https://toolpipe.dev/api/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "algorithm": "sha256"}'
```

Response:
```json
{
  "hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
  "algorithm": "sha256"
}
```

### Supported Algorithms

- `md5` (not recommended for security, fine for checksums)
- `sha1`
- `sha256`
- `sha384`
- `sha512`

### Generate an MD5 Hash

```bash
curl -X POST https://toolpipe.dev/api/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "my-file-contents", "algorithm": "md5"}'
```

### Use Cases

- **File integrity**: Generate checksums for release artifacts
- **Cache busting**: Hash content to create cache keys
- **Data deduplication**: Compare hashes instead of full content
- **Password hashing** (use bcrypt for production, but SHA-256 for quick checks)

### Python: Verify File Integrity

```python
import requests

def get_hash(content, algorithm="sha256"):
    response = requests.post(
        "https://toolpipe.dev/api/hash/generate",
        json={"text": content, "algorithm": algorithm}
    )
    return response.json()["hash"]

# Compare a file against a known hash
with open("release.tar.gz", "r") as f:
    file_hash = get_hash(f.read())

expected = "b94d27b9934d3e08..."
assert file_hash == expected, "File integrity check failed!"
```

### Bash: Quick Checksum Script

```bash
#!/bin/bash
# Generate checksums for all files in a directory
for file in dist/*; do
  content=$(cat "$file")
  hash=$(curl -s -X POST https://toolpipe.dev/api/hash/generate \
    -H "Content-Type: application/json" \
    -d "{\"text\": $(echo "$content" | jq -Rs .), \"algorithm\": \"sha256\"}" \
    | jq -r '.hash')
  echo "$hash  $file"
done
```

## Bonus: Combine All Three

Here is a script that generates a QR code, formats some JSON metadata, and creates a hash of the content:

```bash
#!/bin/bash
URL="https://my-app.com/v2.0"

# Generate QR code
curl -s -X POST https://toolpipe.dev/api/qr/generate \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$URL\", \"size\": 400}" \
  -o release-qr.png

# Format release metadata
METADATA='{"version":"2.0","url":"'$URL'","date":"2026-04-03"}'
FORMATTED=$(curl -s -X POST https://toolpipe.dev/api/json/format \
  -H "Content-Type: application/json" \
  -d "{\"json_string\": \"$(echo $METADATA | sed 's/"/\\"/g')\"}" \
  | jq -r '.formatted')
echo "$FORMATTED" > release-metadata.json

# Hash the metadata for integrity
HASH=$(curl -s -X POST https://toolpipe.dev/api/hash/generate \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$METADATA\", \"algorithm\": \"sha256\"}" \
  | jq -r '.hash')
echo "Release hash: $HASH"
```

## All 220+ Tools

These three APIs are just the start. [ToolPipe](https://toolpipe.dev) has 220+ tools covering:

- **Text**: Base64, URL encode/decode, Markdown to HTML, string utilities
- **Security**: JWT decode, password strength, SSL checker
- **Network**: DNS lookup, WHOIS, HTTP headers
- **Code**: Regex tester, color converter, code review
- **Docker**: Dockerfile analysis, compose validation
- **Time**: Timestamp conversion, timezone tools

Everything is free, no signup required, and available as both a REST API and an [MCP server](https://github.com/COSAI-Labs/toolpipe) for AI agents.

---

Which of these tools do you use most often? What other APIs would save you time? Drop a comment below.
