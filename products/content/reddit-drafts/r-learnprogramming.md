# Reddit Post: r/learnprogramming

**Subreddit:** r/learnprogramming
**Type:** Text post

---

**Title:** Free API with 240+ endpoints you can practice with (no signup, no API key needed)

**Body:**

If you're learning to make API calls (fetch, axios, curl, whatever), here's a free API you can hit without signing up for anything or getting an API key.

**ToolPipe** has 240+ endpoints that actually do useful things, so you're not just hitting a dummy API that returns fake data. Some beginner-friendly examples:

**GET requests (easy, just a URL):**
```
https://toolpipe.dev/api/dns/lookup?domain=google.com
https://toolpipe.dev/api/ip/geo?ip=8.8.8.8
https://toolpipe.dev/api/random/number?min=1&max=100
https://toolpipe.dev/api/uuid/generate
```

**POST requests (practice sending JSON bodies):**
```javascript
// JavaScript fetch example
const response = await fetch('https://toolpipe.dev/api/json/format', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ json_string: '{"name":"test","value":42}' })
});
const data = await response.json();
console.log(data);
```

```python
# Python requests example
import requests
r = requests.post('https://toolpipe.dev/api/hash/sha256',
    json={"text": "hello world"})
print(r.json())
```

**Why this is useful for learning:**
- Real responses with real data (not placeholder text)
- No auth setup to deal with
- CORS enabled, so it works from browser JS projects
- Every endpoint documented with examples at https://toolpipe.dev/docs
- You can build small projects with it (QR code generator, DNS checker, password tool)

**Project ideas using this API:**
1. Build a "developer dashboard" that shows DNS info, SSL status, and WHOIS for any domain
2. Create a text utility app (Base64 encoder, hash generator, UUID maker)
3. Make a QR code generator web page
4. Build a JSON formatter/validator tool

Live: https://toolpipe.dev
Docs: https://toolpipe.dev/docs

Happy to answer questions about how APIs work if anyone's just getting started.
