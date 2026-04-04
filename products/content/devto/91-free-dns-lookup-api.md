---
title: "Free DNS Lookup API: Query A, MX, TXT, NS Records via REST"
published: false
tags: dns, api, networking, devops
---

Query DNS records for any domain without installing dig or nslookup.

```bash
curl "https://toolpipe.dev/dns/lookup?domain=github.com&type=A"
```

## Supported Record Types
- **A**: IPv4 addresses
- **AAAA**: IPv6 addresses
- **MX**: Mail exchange servers
- **TXT**: SPF, DKIM, verification records
- **NS**: Nameservers
- **CNAME**: Canonical names

## Real-World Use Cases

1. **Domain monitoring**: Alert when DNS records change
2. **Email validation**: Check MX records before sending
3. **SSL verification**: Confirm CNAME for cert validation
4. **Migration tracking**: Monitor DNS propagation

No signup, no API key for basic usage. [Full docs](https://toolpipe.dev/docs)
