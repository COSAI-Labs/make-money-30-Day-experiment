---
title: "Free Invoice Generator API - Create PDF Invoices Programmatically"
published: false
tags: ["api", "pdf", "saas", "tools"]
---

Generate professional PDF invoices with a single API call. ToolPipe's Invoice Generator API handles formatting, calculations, and PDF output.

## API Endpoint

```
POST https://toolpipe.dev/invoice
Content-Type: application/json

{
  "from": "Your Company",
  "to": "Client Name",
  "items": [{"description": "Web Development", "quantity": 10, "rate": 150}]
}
```

Returns a downloadable PDF invoice. Supports custom line items, tax calculation, and company details.

No signup required. Docs: [toolpipe.dev/docs](https://toolpipe.dev/docs)
