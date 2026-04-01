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
    { name: "toolpipe", version: "1.2.0" },
    {
      capabilities: { tools: {} },
      instructions: "ToolPipe provides 70+ developer utility APIs. Use these tools for JSON formatting, QR code generation, hashing, UUID generation, DNS lookup, base64 encoding, markdown conversion, text analysis, regex testing, JWT decoding, and more.",
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
    version: "1.2.0",
    protocol: "MCP (Model Context Protocol)",
    transport: "Streamable HTTP",
    tools: 34,
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
  console.log(`34 tools available. API backend: ${API_BASE}`);
});
