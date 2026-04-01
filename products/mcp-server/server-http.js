#!/usr/bin/env node

/**
 * ToolPipe Remote MCP Server (Streamable HTTP Transport)
 *
 * Any AI agent can connect to this server over HTTP to use ToolPipe tools.
 * No npm install needed on the client side.
 *
 * Usage:
 *   node server-http.js
 *   PORT=8090 node server-http.js
 *
 * Connect from Claude Desktop:
 *   { "mcpServers": { "toolpipe": { "url": "https://your-server/mcp" } } }
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { z } from "zod";

const PORT = parseInt(process.env.MCP_PORT || "8090");
const API_BASE = process.env.TOOLPIPE_BASE_URL || "http://localhost:8081";

async function apiCall(path, options = {}) {
  const url = new URL(path, API_BASE);
  const fetchOptions = { headers: { "Content-Type": "application/json" }, ...options };
  const resp = await fetch(url.toString(), fetchOptions);
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
  }
  const contentType = resp.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return await resp.json();
  return await resp.text();
}

function textResult(data) {
  const text = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  return { content: [{ type: "text", text }] };
}

function errorResult(msg) {
  return { content: [{ type: "text", text: msg }], isError: true };
}

function createServer() {
  const server = new McpServer(
    { name: "toolpipe", version: "1.6.0" },
    {
      capabilities: { tools: {} },
      instructions: "ToolPipe provides 110+ developer utility APIs as 51 HTTP MCP tools. JSON formatting, QR codes, hashing, UUID, DNS, base64, markdown, regex testing, JWT decoding, IP geolocation, cron parsing, password checking, color palettes, text diffing, timestamp conversion, and more.",
    }
  );

  // JSON & Data
  server.tool("json_format", "Format, validate, and pretty-print JSON.", { json: z.string() }, async ({ json }) => {
    try { return textResult(JSON.stringify(JSON.parse(json), null, 2)); } catch (e) { return errorResult(`JSON Error: ${e.message}`); }
  });
  server.tool("json_to_yaml", "Convert JSON to YAML.", { json: z.string() }, async ({ json }) => textResult(await apiCall("/api/convert/json-to-yaml", { method: "POST", body: JSON.stringify({ json }) })));
  server.tool("json_to_csv", "Convert JSON array to CSV.", { json: z.string() }, async ({ json }) => textResult(await apiCall("/json/to-csv", { method: "POST", body: JSON.stringify({ json }) })));
  server.tool("json_validate_schema", "Validate JSON against a JSON Schema.", { data: z.string(), schema_def: z.string() }, async ({ data, schema_def }) => textResult(await apiCall("/api/json/validate-schema", { method: "POST", body: JSON.stringify({ data, schema_def }) })));
  server.tool("code_format", "Format code (JSON, SQL, HTML).", { code: z.string(), language: z.string() }, async ({ code, language }) => textResult(await apiCall("/api/code/format", { method: "POST", body: JSON.stringify({ code, language }) })));

  // Text
  server.tool("analyze_text", "Analyze text: word count, reading time, etc.", { text: z.string() }, async ({ text }) => textResult(await apiCall("/text/analyze", { method: "POST", body: JSON.stringify({ text }) })));
  server.tool("summarize_text", "Summarize text (extractive).", { text: z.string(), max_sentences: z.number().optional() }, async ({ text, max_sentences }) => textResult(await apiCall("/api/text/summarize", { method: "POST", body: JSON.stringify({ text, max_sentences: max_sentences || 3 }) })));
  server.tool("detect_language", "Detect text language.", { text: z.string() }, async ({ text }) => textResult(await apiCall("/api/text/detect-language", { method: "POST", body: JSON.stringify({ text }) })));
  server.tool("text_diff", "Compare two texts (unified diff).", { text1: z.string(), text2: z.string() }, async ({ text1, text2 }) => textResult(await apiCall("/api/text/diff", { method: "POST", body: JSON.stringify({ text1, text2 }) })));
  server.tool("slugify", "Convert text to URL-friendly slug.", { text: z.string() }, async ({ text }) => textResult(await apiCall("/api/text/slugify", { method: "POST", body: JSON.stringify({ text }) })));
  server.tool("regex_test", "Test regex pattern against text.", { pattern: z.string(), text: z.string(), flags: z.string().optional() }, async ({ pattern, text, flags }) => textResult(await apiCall("/api/regex/test", { method: "POST", body: JSON.stringify({ pattern, text, flags: flags || "" }) })));
  server.tool("markdown_to_html", "Convert Markdown to HTML.", { markdown: z.string() }, async ({ markdown }) => textResult(await apiCall("/markdown/to-html", { method: "POST", body: JSON.stringify({ markdown }) })));
  server.tool("markdown_table", "Generate markdown table.", { headers: z.array(z.string()), rows: z.array(z.array(z.string())) }, async ({ headers, rows }) => textResult(await apiCall("/api/markdown/table", { method: "POST", body: JSON.stringify({ headers, rows }) })));
  server.tool("lorem_ipsum", "Generate placeholder text.", { paragraphs: z.number().optional() }, async ({ paragraphs }) => textResult(await apiCall("/api/lorem-ipsum", { method: "POST", body: JSON.stringify({ paragraphs: paragraphs || 3 }) })));

  // Encoding & Hashing
  server.tool("hash_text", "Hash text (MD5/SHA).", { text: z.string(), algorithm: z.string().optional() }, async ({ text, algorithm }) => textResult(await apiCall("/hash/generate", { method: "POST", body: JSON.stringify({ text, algorithm: algorithm || "sha256" }) })));
  server.tool("base64_encode_decode", "Base64 encode/decode.", { text: z.string(), action: z.string().optional() }, async ({ text, action }) => textResult(await apiCall("/base64", { method: "POST", body: JSON.stringify({ text, action: action || "encode" }) })));
  server.tool("url_encode_decode", "URL encode/decode.", { text: z.string(), action: z.string().optional() }, async ({ text, action }) => textResult(await apiCall("/api/url/encode-decode", { method: "POST", body: JSON.stringify({ text, action: action || "encode" }) })));
  server.tool("jwt_decode", "Decode JWT token.", { token: z.string() }, async ({ token }) => textResult(await apiCall("/api/jwt/decode", { method: "POST", body: JSON.stringify({ token }) })));
  server.tool("generate_uuid", "Generate UUIDs.", { count: z.number().optional() }, async ({ count }) => textResult(await apiCall(`/uuid/generate?count=${count || 1}`)));
  server.tool("generate_password", "Generate secure passwords.", { length: z.number().optional(), count: z.number().optional() }, async ({ length, count }) => textResult(await apiCall("/api/password/generate", { method: "POST", body: JSON.stringify({ length: length || 16, count: count || 1 }) })));

  // Web & Network
  server.tool("dns_lookup", "DNS lookup for a domain.", { domain: z.string() }, async ({ domain }) => textResult(await apiCall(`/dns/lookup?domain=${encodeURIComponent(domain)}`)));
  server.tool("ip_lookup", "IP geolocation.", { ip: z.string().optional() }, async ({ ip }) => textResult(ip ? await apiCall(`/ip/lookup?ip=${encodeURIComponent(ip)}`) : await apiCall("/ip/my")));
  server.tool("extract_metadata", "Extract URL metadata.", { url: z.string() }, async ({ url }) => textResult(await apiCall(`/meta/extract?url=${encodeURIComponent(url)}`)));
  server.tool("check_website_status", "Check if website is up/down.", { url: z.string() }, async ({ url }) => textResult(await apiCall(`/down/check?url=${encodeURIComponent(url)}`)));
  server.tool("seo_analyze", "SEO analysis of a URL.", { url: z.string() }, async ({ url }) => textResult(await apiCall(`/seo/analyze?url=${encodeURIComponent(url)}`)));
  server.tool("http_request", "Make HTTP request (curl via API).", { url: z.string(), method: z.string().optional(), body: z.string().optional() }, async ({ url, method, body }) => textResult(await apiCall("/api/http/request", { method: "POST", body: JSON.stringify({ url, method: method || "GET", body }) })));
  server.tool("shorten_url", "Create shortened URL.", { url: z.string() }, async ({ url }) => textResult(await apiCall("/s/create", { method: "POST", body: JSON.stringify({ url }) })));

  // Utilities
  server.tool("generate_qr_code", "Generate QR code URL.", { text: z.string(), size: z.number().optional() }, async ({ text, size }) => textResult(`QR Code URL: ${API_BASE}/qr/generate?text=${encodeURIComponent(text)}&size=${size || 200}`));
  server.tool("color_convert", "Convert colors (HEX/RGB/HSL).", { color: z.string() }, async ({ color }) => textResult(await apiCall(`/color/convert?color=${encodeURIComponent(color)}`)));
  server.tool("timestamp_convert", "Convert timestamps/dates.", { timestamp: z.number().optional(), date_string: z.string().optional() }, async ({ timestamp, date_string }) => {
    if (!timestamp && !date_string) return textResult(await apiCall("/api/timestamp/now"));
    const body = {};
    if (timestamp) body.timestamp = timestamp;
    if (date_string) body.date_string = date_string;
    return textResult(await apiCall("/api/timestamp/convert", { method: "POST", body: JSON.stringify(body) }));
  });
  server.tool("cron_parse", "Parse cron expression to English.", { expression: z.string() }, async ({ expression }) => textResult(await apiCall("/api/cron/parse", { method: "POST", body: JSON.stringify({ expression }) })));
  server.tool("get_crypto_prices", "Live crypto prices.", { coins: z.string().optional() }, async ({ coins }) => textResult(await apiCall(`/api/crypto/prices${coins ? `?coins=${encodeURIComponent(coins)}` : ""}`)));
  server.tool("css_minify", "Minify CSS.", { css: z.string() }, async ({ css }) => textResult(await apiCall("/api/css/minify", { method: "POST", body: JSON.stringify({ css }) })));
  server.tool("js_minify", "Minify JavaScript.", { code: z.string() }, async ({ code }) => textResult(await apiCall("/api/js/minify", { method: "POST", body: JSON.stringify({ code }) })));

  // v1.4.0 new tools
  server.tool("web_extract", "Extract content from web pages (text, links, images, metadata, structured).", { url: z.string(), extract: z.string().optional() }, async ({ url, extract }) => textResult(await apiCall("/api/web/extract", { method: "POST", body: JSON.stringify({ url, extract: extract || "text" }) })));
  server.tool("code_analyze", "Analyze code: detect language, find functions/classes, measure complexity.", { code: z.string(), language: z.string().optional() }, async ({ code, language }) => textResult(await apiCall("/api/code/analyze", { method: "POST", body: JSON.stringify({ code, language: language || "auto" }) })));
  server.tool("schema_generate", "Generate TypeScript, Python, Zod, or JSON Schema from JSON data.", { data: z.string(), format: z.string().optional() }, async ({ data, format }) => textResult(await apiCall("/api/schema/generate", { method: "POST", body: JSON.stringify({ data, format: format || "typescript" }) })));
  server.tool("prompt_build", "Build structured LLM prompts with variable substitution.", { template: z.string(), variables: z.record(z.string()).optional(), system: z.string().optional() }, async ({ template, variables, system }) => textResult(await apiCall("/api/prompt/build", { method: "POST", body: JSON.stringify({ template, variables: variables || {}, system: system || "" }) })));
  server.tool("test_endpoint", "Test API endpoints with detailed response metrics and timing.", { url: z.string(), method: z.string().optional(), headers: z.record(z.string()).optional(), body: z.string().optional() }, async ({ url, method, headers, body }) => textResult(await apiCall("/api/test/endpoint", { method: "POST", body: JSON.stringify({ url, method: method || "GET", headers: headers || {}, body: body || "" }) })));
  server.tool("text_similarity", "Calculate text similarity (Jaccard, cosine, character-level).", { text1: z.string(), text2: z.string() }, async ({ text1, text2 }) => textResult(await apiCall("/api/text/similarity", { method: "POST", body: JSON.stringify({ text1, text2 }) })));

  // v1.5.0 new tools
  server.tool("ip_lookup", "Look up IP geolocation, ISP, and network info.", { ip: z.string() }, async ({ ip }) => textResult(await apiCall(`/api/ip/lookup?ip=${encodeURIComponent(ip)}`)));
  server.tool("text_diff", "Generate unified diff between two texts.", { original: z.string(), modified: z.string(), context_lines: z.number().optional() }, async ({ original, modified, context_lines }) => textResult(await apiCall("/api/diff/text", { method: "POST", body: JSON.stringify({ original, modified, context_lines: context_lines || 3 }) })));
  server.tool("jwt_decode", "Decode JWT tokens without verification.", { token: z.string() }, async ({ token }) => textResult(await apiCall("/api/jwt/decode", { method: "POST", body: JSON.stringify({ token }) })));
  server.tool("time_convert", "Convert timestamps (Unix, ISO 8601, human-readable).", { timestamp: z.string().optional() }, async ({ timestamp }) => textResult(await apiCall(`/api/time/convert${timestamp ? `?timestamp=${encodeURIComponent(timestamp)}` : ""}`)));
  server.tool("headers_analyze", "Analyze HTTP response headers for security and caching.", { url: z.string() }, async ({ url }) => textResult(await apiCall(`/api/headers/analyze?url=${encodeURIComponent(url)}`)));
  server.tool("password_check", "Check password strength with entropy and crack time.", { password: z.string() }, async ({ password }) => textResult(await apiCall("/api/password/check", { method: "POST", body: JSON.stringify({ password }) })));
  server.tool("regex_test", "Test regex patterns with match details and groups.", { pattern: z.string(), text: z.string(), flags: z.string().optional() }, async ({ pattern, text, flags }) => textResult(await apiCall("/api/regex/test", { method: "POST", body: JSON.stringify({ pattern, text, flags: flags || "" }) })));
  server.tool("lorem_ipsum", "Generate lorem ipsum placeholder text.", { paragraphs: z.number().optional(), format: z.string().optional() }, async ({ paragraphs, format }) => textResult(await apiCall(`/api/lorem?paragraphs=${paragraphs || 3}&format=${format || "text"}`)));
  server.tool("color_palette", "Generate color palettes from a base color.", { base_color: z.string(), scheme: z.string().optional(), count: z.number().optional() }, async ({ base_color, scheme, count }) => textResult(await apiCall(`/api/color/palette?base_color=${encodeURIComponent(base_color)}&scheme=${scheme || "complementary"}&count=${count || 5}`)));
  server.tool("slug_generate", "Generate URL-friendly slugs.", { text: z.string(), separator: z.string().optional() }, async ({ text, separator }) => textResult(await apiCall("/api/slug/generate", { method: "POST", body: JSON.stringify({ text, separator: separator || "-" }) })));
  server.tool("markdown_strip", "Strip markdown formatting to plain text.", { markdown: z.string() }, async ({ markdown }) => textResult(await apiCall("/api/markdown/strip", { method: "POST", body: JSON.stringify({ markdown }) })));

  // AI Agent Utility Tools
  server.tool("extract_structured", "Extract emails, URLs, phones, dates, numbers from text.", { text: z.string(), extract: z.string().optional() }, async ({ text, extract }) => textResult(await apiCall("/api/extract/structured", { method: "POST", body: JSON.stringify({ text, extract: extract || "all" }) })));
  server.tool("text_transform", "Apply text transforms: uppercase, lowercase, title, reverse, sort_lines, unique_lines, trim.", { text: z.string(), transforms: z.array(z.string()) }, async ({ text, transforms }) => textResult(await apiCall("/api/text/transform", { method: "POST", body: JSON.stringify({ text, transforms }) })));
  server.tool("text_compare", "Compare strings for similarity using Levenshtein distance.", { items: z.array(z.string()) }, async ({ items }) => textResult(await apiCall("/api/text/compare", { method: "POST", body: JSON.stringify({ items }) })));
  server.tool("convert_units", "Convert units: length, weight, temperature, volume, speed, data.", { value: z.number(), from_unit: z.string(), to_unit: z.string() }, async ({ value, from_unit, to_unit }) => textResult(await apiCall("/api/convert/units", { method: "POST", body: JSON.stringify({ value, from_unit, to_unit }) })));

  // New tools: Batch 3 (session 17)
  server.tool("sql_format", "Format and prettify SQL queries.", { sql: z.string(), uppercase_keywords: z.boolean().optional() }, async ({ sql, uppercase_keywords }) => textResult(await apiCall("/api/sql/format", { method: "POST", body: JSON.stringify({ sql, uppercase_keywords: uppercase_keywords ?? true }) })));
  server.tool("html_strip", "Strip HTML tags to plain text.", { html: z.string(), preserve_links: z.boolean().optional() }, async ({ html, preserve_links }) => textResult(await apiCall("/api/html/strip", { method: "POST", body: JSON.stringify({ html, preserve_links: preserve_links ?? false }) })));
  server.tool("text_stats", "Text statistics: word count, reading time, readability scores.", { text: z.string() }, async ({ text }) => textResult(await apiCall("/api/text/stats", { method: "POST", body: JSON.stringify({ text }) })));
  server.tool("number_format", "Format numbers: comma, words, roman, scientific, binary, hex.", { number: z.number(), format: z.string().optional() }, async ({ number, format }) => textResult(await apiCall("/api/number/format", { method: "POST", body: JSON.stringify({ number, format: format ?? "all" }) })));
  server.tool("xml_to_json", "Convert XML to JSON.", { xml: z.string() }, async ({ xml }) => textResult(await apiCall("/api/xml/to-json", { method: "POST", body: JSON.stringify({ xml }) })));
  server.tool("yaml_validate", "Validate YAML and convert to JSON.", { yaml_text: z.string() }, async ({ yaml_text }) => textResult(await apiCall("/api/yaml/validate", { method: "POST", body: JSON.stringify({ yaml_text }) })));
  server.tool("env_parse", "Parse .env file content to JSON.", { env_text: z.string() }, async ({ env_text }) => textResult(await apiCall("/api/env/parse", { method: "POST", body: JSON.stringify({ env_text }) })));
  server.tool("http_status", "Get info about an HTTP status code.", { code: z.number() }, async ({ code }) => textResult(await apiCall(`/api/http-status/${code}`)));
  server.tool("jwt_create", "Create a JWT token for testing.", { payload: z.string(), secret: z.string().optional() }, async ({ payload, secret }) => textResult(await apiCall("/api/jwt/create", { method: "POST", body: JSON.stringify({ payload: JSON.parse(payload), secret: secret ?? "your-secret-key" }) })));
  server.tool("my_ip", "Get caller's IP address.", {}, async () => textResult(await apiCall("/api/myip")));

  // API Key & Payment Management (self-service for AI agents)
  server.tool("register_api_key", "Register a free API key (100 calls/day).", { email: z.string() }, async ({ email }) => textResult(await apiCall("/api-keys/register", { method: "POST", body: JSON.stringify({ email }) })));
  server.tool("check_api_usage", "Check API key usage and remaining quota.", { api_key: z.string().optional(), email: z.string().optional() }, async ({ api_key, email }) => { const p = new URLSearchParams(); if (api_key) p.set("api_key", api_key); if (email) p.set("email", email); return textResult(await apiCall(`/api-keys/usage?${p.toString()}`)); });
  server.tool("create_payment", "Create crypto payment order for Pro ($9.99) or Enterprise ($49.99).", { email: z.string(), tier: z.enum(["pro", "enterprise"]) }, async ({ email, tier }) => textResult(await apiCall("/payments/create", { method: "POST", body: JSON.stringify({ email, tier }) })));
  server.tool("verify_payment", "Verify crypto payment on-chain and upgrade API key.", { order_id: z.string(), tx_hash: z.string() }, async ({ order_id, tx_hash }) => textResult(await apiCall("/payments/verify-tx", { method: "POST", body: JSON.stringify({ order_id, tx_hash }) })));
  server.tool("get_pricing", "Get API pricing tiers and payment info.", {}, async () => textResult(await apiCall("/api/pricing")));

  return server;
}

const app = express();
app.use(express.json());

// CORS for remote access
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept, Mcp-Session-Id");
  res.setHeader("Access-Control-Expose-Headers", "Mcp-Session-Id");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

// Health check
app.get("/", (req, res) => {
  res.json({
    name: "ToolPipe MCP Server",
    version: "1.6.0",
    protocol: "MCP (Model Context Protocol)",
    transport: "Streamable HTTP",
    tools: 70,
    endpoint: "/mcp",
    docs: "https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server",
  });
});

// Stateless MCP endpoint: each request creates a fresh server+transport
app.post("/mcp", async (req, res) => {
  const server = createServer();
  try {
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
    res.on("close", () => {
      transport.close();
      server.close();
    });
  } catch (error) {
    console.error("MCP error:", error);
    if (!res.headersSent) {
      res.status(500).json({ jsonrpc: "2.0", error: { code: -32603, message: "Internal server error" }, id: null });
    }
  }
});

// Reject other methods on /mcp
app.get("/mcp", (req, res) => res.status(405).json({ jsonrpc: "2.0", error: { code: -32000, message: "Method not allowed. Use POST." }, id: null }));
app.delete("/mcp", (req, res) => res.status(405).json({ jsonrpc: "2.0", error: { code: -32000, message: "Method not allowed." }, id: null }));

app.listen(PORT, () => {
  console.log(`ToolPipe MCP Server (HTTP) running on http://0.0.0.0:${PORT}/mcp`);
  console.log(`60 tools available. API backend: ${API_BASE}`);
});
