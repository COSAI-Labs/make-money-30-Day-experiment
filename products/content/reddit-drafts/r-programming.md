# Reddit Post: r/programming

**Subreddit:** r/programming
**Type:** Link post or text post

---

**Title:** Free REST API for common dev utilities: UUID, hashing, Base64, DNS lookup, and 140+ more (no auth needed)

**Body:**

I built a REST API that bundles 145+ common developer utility functions into a single service. No API key required for the free tier.

The problem it solves: when you are scripting or building CI/CD pipelines, you sometimes need a quick UUID, a hash, a DNS lookup, or a Base64 encode. You can install a library for each, or you can hit one API.

Example usage in a shell script:

```bash
# Generate a UUID for a deployment ID
DEPLOY_ID=$(curl -s https://troops-submission-what-stays.trycloudflare.com/api/uuid/generate | jq -r '.uuid')

# Hash a config file to check for changes
HASH=$(curl -s -X POST https://troops-submission-what-stays.trycloudflare.com/api/hash/sha256 \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat config.yaml)\"}" | jq -r '.hash')

# Quick DNS check before deployment
curl -s "https://troops-submission-what-stays.trycloudflare.com/api/dns/lookup?domain=myapp.com"
```

In Python:

```python
import requests

# Generate fake test data
resp = requests.get("https://troops-submission-what-stays.trycloudflare.com/api/fake/user")
test_user = resp.json()

# Validate JSON schema
resp = requests.post("https://troops-submission-what-stays.trycloudflare.com/api/json/validate", 
    json={"data": my_data, "schema": my_schema})
```

Full list of endpoints at: https://troops-submission-what-stays.trycloudflare.com/docs

Everything is CORS-enabled. Rate limit is 100 requests/day per IP on the free tier, which covers most scripting use cases.

Source code: https://github.com/COSAI-Labs/make-money-30day-challenge
