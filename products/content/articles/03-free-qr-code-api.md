---
title: "The Simplest Free QR Code API for Developers"
published: false
tags: api, webdev, qrcode, tutorial
canonical_url: https://assessing-scoop-authorities-sheet.trycloudflare.com
---

Need to generate QR codes in your app? Here's the simplest API I've found (because I built it).

## One GET Request

```
https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=https://example.com&size=300
```

That's it. Returns a PNG image. No API key, no signup, no rate limit hassles (100/day free).

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | required | Content to encode |
| `size` | 200 | Image size in pixels |
| `format` | png | Output format (png, svg) |

## Examples

### HTML Image Tag
```html
<img src="https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=https://mysite.com&size=200" alt="QR Code">
```

### Dynamic QR in React
```jsx
function QRCode({ url, size = 200 }) {
  return (
    <img
      src={`https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=${encodeURIComponent(url)}&size=${size}`}
      alt="QR Code"
      width={size}
      height={size}
    />
  );
}
```

### Generate via curl
```bash
curl "https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=Hello+World&size=400" -o qr.png
```

### POST for More Control
```bash
curl -X POST https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "https://example.com", "size": 300}'
```

## WiFi QR Codes

Generate a QR code that connects to WiFi:
```
https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=WIFI:T:WPA;S:MyNetwork;P:MyPassword;;
```

## vCard QR Codes

```
https://assessing-scoop-authorities-sheet.trycloudflare.com/qr/generate?text=BEGIN:VCARD%0AFULL%20NAME:John%20Doe%0ATEL:555-1234%0AEND:VCARD
```

## Why Not Google Charts?

Google's QR API was deprecated. Other alternatives either require signup, have aggressive rate limits, or inject tracking.

ToolPipe's QR API: no signup, no tracking, 100 free calls/day, consistent and reliable.

## Need More?

ToolPipe has 200+ other developer APIs alongside QR codes. Check out [toolpipe.dev](https://assessing-scoop-authorities-sheet.trycloudflare.com) for the full list.

Free API key for higher limits: `POST https://assessing-scoop-authorities-sheet.trycloudflare.com/api-keys/register` with `{"email": "you@example.com"}`.
