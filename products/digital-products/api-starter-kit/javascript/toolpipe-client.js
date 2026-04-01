/**
 * ToolPipe API JavaScript/Node.js Client
 * Complete SDK for all ToolPipe API endpoints.
 */

class ToolPipeClient {
  constructor({ baseUrl = 'https://toolpipe.dev', apiKey = null, timeout = 30000, maxRetries = 3 } = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.timeout = timeout;
    this.maxRetries = maxRetries;
  }

  _headers() {
    const h = { 'User-Agent': 'ToolPipe-JS/1.0' };
    if (this.apiKey) h['Authorization'] = `Bearer ${this.apiKey}`;
    return h;
  }

  async _request(method, path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        const resp = await fetch(url, {
          method,
          headers: { ...this._headers(), ...options.headers },
          body: options.body,
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        if (resp.status === 429) {
          await new Promise(r => setTimeout(r, Math.min(2 ** attempt * 1000, 30000)));
          continue;
        }
        if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
        return resp;
      } catch (err) {
        if (attempt === this.maxRetries - 1) throw err;
        await new Promise(r => setTimeout(r, 2 ** attempt * 1000));
      }
    }
  }

  // --- QR Code ---

  async generateQR(data, size = 300) {
    const resp = await this._request('POST', '/qr/generate', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, size }),
    });
    return resp.arrayBuffer();
  }

  // --- Metadata ---

  async extractMetadata(url) {
    const resp = await this._request('GET', `/meta/extract?url=${encodeURIComponent(url)}`);
    return resp.json();
  }

  // --- Text Analysis ---

  async analyzeText(text) {
    const resp = await this._request('POST', '/text/analyze', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return resp.json();
  }

  // --- Markdown ---

  async markdownToHtml(markdown) {
    const resp = await this._request('POST', '/markdown/to-html', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ markdown }),
    });
    return resp.json();
  }

  // --- Hash ---

  async generateHash(text, algorithm = 'sha256') {
    const resp = await this._request('POST', '/hash/generate', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, algorithm }),
    });
    return resp.json();
  }

  // --- UUID ---

  async generateUUID(count = 1) {
    const resp = await this._request('GET', `/uuid/generate?count=${count}`);
    return resp.json();
  }

  // --- DNS ---

  async dnsLookup(domain) {
    const resp = await this._request('GET', `/dns/lookup?domain=${encodeURIComponent(domain)}`);
    return resp.json();
  }

  // --- SEO ---

  async analyzeSEO(url) {
    const resp = await this._request('GET', `/seo/analyze?url=${encodeURIComponent(url)}`);
    return resp.json();
  }

  // --- URL Shortener ---

  async shortenURL(url, customCode = null) {
    const payload = { url };
    if (customCode) payload.code = customCode;
    const resp = await this._request('POST', '/s/create', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return resp.json();
  }

  // --- Is It Down ---

  async checkDown(url) {
    const resp = await this._request('GET', `/down/check?url=${encodeURIComponent(url)}`);
    return resp.json();
  }

  // --- IP Lookup ---

  async ipLookup(ip) {
    const resp = await this._request('GET', `/ip/lookup?ip=${encodeURIComponent(ip)}`);
    return resp.json();
  }

  async myIP() {
    const resp = await this._request('GET', '/ip/my');
    return resp.json();
  }

  // --- JSON/CSV ---

  async jsonToCsv(data) {
    const resp = await this._request('POST', '/json/to-csv', {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data }),
    });
    return resp.text();
  }
}

// ESM export
export default ToolPipeClient;

// Usage example
async function main() {
  const client = new ToolPipeClient();

  const text = await client.analyzeText('Hello world, testing the ToolPipe API!');
  console.log('Text analysis:', text);

  const dns = await client.dnsLookup('google.com');
  console.log('DNS:', dns);

  const uuids = await client.generateUUID(3);
  console.log('UUIDs:', uuids);
}

// main().catch(console.error);
