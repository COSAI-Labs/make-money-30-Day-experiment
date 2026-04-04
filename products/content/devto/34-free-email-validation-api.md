---
title: "Free Email Validation API: Check Format, MX Records, Disposable Emails"
published: false
tags: api, email, validation, webdev
canonical_url: https://toolpipe.dev
---

Validate email addresses for format correctness, MX records, and disposable email detection via a REST API.

## Usage

```bash
curl -X POST https://toolpipe.dev/email/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Checks Performed

- **Format validation** - RFC 5322 compliance
- **MX record verification** - Domain has mail servers
- **Disposable detection** - Flag temporary email addresses
- **Typo suggestions** - Catch common domain misspellings

## Why Validate Emails?

- Reduce bounce rates
- Prevent fake signups
- Improve deliverability
- Clean your mailing lists
- Save on email service costs

## Part of ToolPipe

120+ free developer tools at [toolpipe.dev](https://toolpipe.dev). No signup needed for the free tier.

**Links:** [API](https://toolpipe.dev) | [MCP Server](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server) | [GitHub](https://github.com/COSAI-Labs/toolpipe-mcp-server)
