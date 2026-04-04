---
title: "Free WHOIS and SSL Certificate APIs for DevOps Teams"
published: false
description: "Monitor domain registrations and SSL certificate expiration with free APIs from ToolPipe. No signup, no API keys, no rate limits."
tags: devops, api, ssl, webdev
canonical_url: https://toolpipe.dev
---

# Free WHOIS and SSL Certificate APIs for DevOps Teams

If you manage more than a handful of domains, you already know the pain. Checking SSL expiration dates one by one through browser UIs. Manually running `whois` on the command line for each domain in your portfolio. Forgetting to renew a certificate until your monitoring alerts fire at 3 AM.

There is a better way. ToolPipe provides free WHOIS lookup and SSL certificate checking APIs that you can integrate into your DevOps workflows in minutes. No signup, no API keys, no credit cards.

## WHOIS Lookup API

Get domain registration details with a single HTTP call:

```bash
curl "https://toolpipe.dev/api/whois/lookup?domain=example.com"
```

The response includes:
- Registrar name and URL
- Domain creation and expiration dates
- Nameserver records
- Registrant information (when publicly available)
- Domain status codes

### Practical Use: Domain Expiration Monitoring

Build a simple monitoring script that checks all your domains:

```bash
#!/bin/bash
DOMAINS=("myapp.com" "api.myapp.com" "staging.myapp.com")

for domain in "${DOMAINS[@]}"; do
  result=$(curl -s "https://toolpipe.dev/api/whois/lookup?domain=$domain")
  expiry=$(echo "$result" | jq -r '.expiryDate')
  echo "$domain expires: $expiry"
done
```

Run this on a weekly cron job and pipe the output to Slack or email. You will never miss an expiration again.

## SSL Certificate Checker API

Check any domain's SSL certificate details:

```bash
curl "https://toolpipe.dev/api/ssl/check?domain=github.com"
```

The JSON response includes:
- Certificate issuer and subject
- Validity period (not before / not after)
- Days until expiration
- Protocol version and cipher suite
- Whether the certificate chain is valid

### Practical Use: CI/CD Certificate Validation

Add SSL checks to your deployment pipeline. Here is a GitHub Actions step that fails the build if any certificate expires within 14 days:

```yaml
- name: Check SSL Certificates
  run: |
    for domain in myapp.com api.myapp.com; do
      days=$(curl -s "https://toolpipe.dev/api/ssl/check?domain=$domain" | jq '.daysUntilExpiry')
      echo "$domain: $days days remaining"
      if [ "$days" -lt 14 ]; then
        echo "::error::SSL certificate for $domain expires in $days days!"
        exit 1
      fi
    done
```

This catches certificate problems before they become production incidents.

## Combining WHOIS and SSL for Complete Domain Monitoring

The most effective monitoring checks both domain registration and SSL certificates together. Build a dashboard that tracks:

1. Domain expiration dates (from WHOIS)
2. SSL certificate expiration (from SSL check)
3. DNS record changes (using the DNS lookup API at `/api/dns/lookup`)

All three APIs are free and available on ToolPipe with no signup required.

## Node.js Integration

For more sophisticated monitoring, use these APIs in a Node.js service:

```javascript
async function checkDomain(domain) {
  const [whois, ssl] = await Promise.all([
    fetch(`https://toolpipe.dev/api/whois/lookup?domain=${domain}`).then(r => r.json()),
    fetch(`https://toolpipe.dev/api/ssl/check?domain=${domain}`).then(r => r.json())
  ]);

  return {
    domain,
    domainExpiry: whois.expiryDate,
    sslDaysLeft: ssl.daysUntilExpiry,
    sslIssuer: ssl.issuer
  };
}
```

## 120+ Tools for AI Agents

ToolPipe also offers an MCP (Model Context Protocol) server that gives AI coding agents direct access to WHOIS, SSL checking, and 118 other developer tools:

```bash
npx @cosai-labs/toolpipe-mcp-server@latest
```

Add it to your Claude Desktop, Cursor, or any MCP-compatible editor. Your AI assistant can then check certificates, look up domains, and run dozens of other DevOps utilities without leaving your editor.

## Getting Started

All ToolPipe APIs are completely free with no signup:

- WHOIS: `https://toolpipe.dev/api/whois/lookup?domain=DOMAIN`
- SSL Check: `https://toolpipe.dev/api/ssl/check?domain=DOMAIN`
- DNS Lookup: `https://toolpipe.dev/api/dns/lookup?domain=DOMAIN`
- Full API docs: [https://toolpipe.dev](https://toolpipe.dev)

Start building your domain monitoring pipeline today. Your on-call team will thank you.
