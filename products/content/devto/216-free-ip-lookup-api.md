---
title: "Free IP Lookup and My IP API"
published: false
tags: ["api", "ip", "geolocation", "networking"]
---

## Free IP Lookup API

Two endpoints: get your own IP, or look up geolocation for any IP address.

### Endpoints

```
GET https://toolpipe.dev/ip/my
GET https://toolpipe.dev/ip/lookup?ip=8.8.8.8
```

### Geolocation Data

- Country, region, city
- Latitude and longitude
- ISP and organization
- Timezone

### Example

```bash
# Get your IP
curl https://toolpipe.dev/ip/my

# Look up an IP
curl "https://toolpipe.dev/ip/lookup?ip=1.1.1.1"
```

### Use Cases

- Geo-targeting in applications
- Security logging and audit trails
- Network diagnostics
- Content localization

No API key required. Free at [toolpipe.dev](https://toolpipe.dev).
