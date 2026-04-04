---
title: "Free Fake Data Generator API: Realistic Test Data via REST"
published: false
tags: testing, api, devtools, fakedata
---

Stop hardcoding test data. ToolPipe's Fake Data API generates realistic names, emails, addresses, phone numbers, and more for your tests.

## Quick Start

```bash
curl -X POST https://toolpipe.dev/fake-data/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "user", "count": 10}'
```

## Data Types

- Users (name, email, avatar, bio)
- Addresses (street, city, state, zip, country)
- Companies (name, industry, revenue)
- Products (name, price, description, SKU)
- Financial (credit cards, IBANs, BTC addresses)

## No Signup Required

Free, no rate limits on basic tier.

## Also Available As MCP Server

```bash
npx @cosai-labs/toolpipe-mcp-server
```

[API docs](https://toolpipe.dev/docs) | [npm](https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server)
