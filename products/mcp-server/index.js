#!/usr/bin/env node

/**
 * ToolPipe MCP Server
 *
 * Exposes 120+ developer utility tools via Model Context Protocol.
 * AI agents can discover and use these tools for JSON formatting,
 * QR code generation, hashing, UUID generation, DNS lookup, and more.
 *
 * Usage:
 *   npx @toolpipe/mcp-server
 *   TOOLPIPE_API_KEY=tp_xxx npx @toolpipe/mcp-server
 *   TOOLPIPE_BASE_URL=https://your-instance.com npx @toolpipe/mcp-server
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { createHash, randomUUID } from "node:crypto";

const BASE_URL = process.env.TOOLPIPE_BASE_URL || "https://toolpipe.dev";
const API_KEY = process.env.TOOLPIPE_API_KEY || "";
const LOCAL_MODE = process.env.TOOLPIPE_LOCAL === "true";

async function apiCall(path, options = {}) {
  const url = new URL(path, BASE_URL);
  if (API_KEY) url.searchParams.set("api_key", API_KEY);

  const fetchOptions = { headers: { "Content-Type": "application/json" }, ...options };
  if (API_KEY) fetchOptions.headers["X-API-Key"] = API_KEY;

  const resp = await fetch(url.toString(), fetchOptions);
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
  }

  const contentType = resp.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return await resp.json();
  }
  return await resp.text();
}

function textResult(data) {
  const text = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  return { content: [{ type: "text", text }] };
}

function errorResult(msg) {
  return { content: [{ type: "text", text: msg }], isError: true };
}

const server = new McpServer(
  { name: "toolpipe", version: "1.15.0" },
  {
    capabilities: { tools: {} },
    instructions: "ToolPipe provides 200+ developer utility APIs as 120+ MCP tools. JSON formatting, QR codes, hashing, UUID, DNS, base64, SQL formatting, XML/YAML conversion, text stats, HTML stripping, number formatting, .env parsing, HTTP status codes, JWT create/decode, IP info, regex testing, password checking, color palettes, text diffing, placeholder images, favicon extraction, sitemap generation, README generation, CSS gradients, meta tags, robots.txt, htaccess, and more. Free: 100 calls/day (no signup). Pro: 10,000 calls/day ($9.99).",
  }
);

// --- Tool Definitions ---

// --- Local implementations for offline/fast mode ---
function localHash(text, algorithm = "sha256") {
  const algo = algorithm.toLowerCase().replace("-", "");
  return createHash(algo).update(text).digest("hex");
}

function localBase64(text, action = "encode") {
  if (action === "decode") return Buffer.from(text, "base64").toString("utf-8");
  return Buffer.from(text).toString("base64");
}

function localUUID(count = 1) {
  return Array.from({ length: Math.min(count, 100) }, () => randomUUID());
}

server.tool(
  "json_format",
  "Format, validate, and pretty-print JSON. Detects syntax errors.",
  { json: z.string().describe("JSON string to format") },
  async ({ json }) => {
    try {
      const parsed = JSON.parse(json);
      return textResult(JSON.stringify(parsed, null, 2));
    } catch (e) {
      return errorResult(`JSON Error: ${e.message}`);
    }
  }
);

server.tool(
  "generate_qr_code",
  "Generate a QR code image URL from text or a URL.",
  {
    text: z.string().describe("Text or URL to encode"),
    size: z.number().optional().describe("Image size in pixels (default 200)"),
  },
  async ({ text, size }) => {
    const s = size || 200;
    const url = `${BASE_URL}/qr/generate?text=${encodeURIComponent(text)}&size=${s}`;
    return textResult(`QR Code URL: ${url}`);
  }
);

server.tool(
  "generate_uuid",
  "Generate one or more UUIDs (v4).",
  { count: z.number().optional().describe("Number of UUIDs to generate (default 1, max 100)") },
  async ({ count }) => {
    const uuids = localUUID(count || 1);
    return textResult(uuids.length === 1 ? { uuid: uuids[0] } : { uuids, count: uuids.length });
  }
);

server.tool(
  "hash_text",
  "Generate hash of text using MD5, SHA-1, SHA-256, or SHA-512.",
  {
    text: z.string().describe("Text to hash"),
    algorithm: z.string().optional().describe("Hash algorithm: md5, sha1, sha256, sha512 (default sha256)"),
  },
  async ({ text, algorithm }) => {
    const algo = algorithm || "sha256";
    const hash = localHash(text, algo);
    return textResult({ text: text.substring(0, 50), algorithm: algo, hash });
  }
);

server.tool(
  "base64_encode_decode",
  "Encode or decode Base64 strings.",
  {
    text: z.string().describe("Text to encode or decode"),
    action: z.string().optional().describe("'encode' or 'decode' (default encode)"),
  },
  async ({ text, action }) => {
    const act = action || "encode";
    const result = localBase64(text, act);
    return textResult({ action: act, input: text.substring(0, 50), result });
  }
);

server.tool(
  "dns_lookup",
  "Perform DNS lookup for a domain. Returns A, AAAA, MX, NS, TXT records.",
  { domain: z.string().describe("Domain name to look up") },
  async ({ domain }) => {
    const result = await apiCall(`/dns/lookup?domain=${encodeURIComponent(domain)}`);
    return textResult(result);
  }
);

server.tool(
  "markdown_to_html",
  "Convert Markdown text to HTML.",
  { markdown: z.string().describe("Markdown text to convert") },
  async ({ markdown }) => {
    const result = await apiCall("/markdown/to-html", {
      method: "POST",
      body: JSON.stringify({ markdown }),
    });
    return textResult(result);
  }
);

server.tool(
  "analyze_text",
  "Analyze text: word count, character count, reading time, sentence count, and more.",
  { text: z.string().describe("Text to analyze") },
  async ({ text }) => {
    const result = await apiCall("/text/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    return textResult(result);
  }
);

server.tool(
  "css_minify",
  "Minify CSS code to reduce file size.",
  { css: z.string().describe("CSS code to minify") },
  async ({ css }) => {
    const result = await apiCall("/api/css/minify", {
      method: "POST",
      body: JSON.stringify({ css }),
    });
    return textResult(result);
  }
);

server.tool(
  "js_minify",
  "Minify JavaScript code to reduce file size.",
  { code: z.string().describe("JavaScript code to minify") },
  async ({ code }) => {
    const result = await apiCall("/api/js/minify", {
      method: "POST",
      body: JSON.stringify({ code }),
    });
    return textResult(result);
  }
);

server.tool(
  "json_to_yaml",
  "Convert JSON to YAML format.",
  { json: z.string().describe("JSON string to convert to YAML") },
  async ({ json }) => {
    const result = await apiCall("/api/convert/json-to-yaml", {
      method: "POST",
      body: JSON.stringify({ json }),
    });
    return textResult(result);
  }
);

server.tool(
  "json_to_csv",
  "Convert JSON array to CSV format.",
  { json: z.string().describe("JSON array string to convert to CSV") },
  async ({ json }) => {
    const result = await apiCall("/json/to-csv", {
      method: "POST",
      body: JSON.stringify({ json }),
    });
    return textResult(result);
  }
);

server.tool(
  "color_convert",
  "Convert colors between HEX, RGB, and HSL formats.",
  {
    color: z.string().describe("Color value (e.g., #ff6600, rgb(255,102,0))"),
    format: z.string().optional().describe("Target format: hex, rgb, hsl"),
  },
  async ({ color, format }) => {
    let url = `/color/convert?color=${encodeURIComponent(color)}`;
    if (format) url += `&format=${format}`;
    const result = await apiCall(url);
    return textResult(result);
  }
);

server.tool(
  "extract_metadata",
  "Extract metadata (title, description, Open Graph, Twitter cards) from a URL.",
  { url: z.string().describe("URL to extract metadata from") },
  async ({ url }) => {
    const result = await apiCall(`/meta/extract?url=${encodeURIComponent(url)}`);
    return textResult(result);
  }
);

server.tool(
  "ip_lookup",
  "Look up geolocation and ISP info for an IP address.",
  { ip: z.string().optional().describe("IP address to look up (omit for your own IP)") },
  async ({ ip }) => {
    const result = ip
      ? await apiCall(`/ip/lookup?ip=${encodeURIComponent(ip)}`)
      : await apiCall("/ip/my");
    return textResult(result);
  }
);

server.tool(
  "check_website_status",
  "Check if a website is up or down.",
  { url: z.string().describe("URL to check") },
  async ({ url }) => {
    const result = await apiCall(`/down/check?url=${encodeURIComponent(url)}`);
    return textResult(result);
  }
);

server.tool(
  "shorten_url",
  "Create a shortened URL.",
  {
    url: z.string().describe("URL to shorten"),
    custom_code: z.string().optional().describe("Optional custom short code"),
  },
  async ({ url, custom_code }) => {
    const body = { url };
    if (custom_code) body.custom_code = custom_code;
    const result = await apiCall("/s/create", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return textResult(result);
  }
);

server.tool(
  "get_random_quote",
  "Get a random inspirational or programming quote.",
  {},
  async () => {
    const result = await apiCall("/api/random/quote");
    return textResult(result);
  }
);

server.tool(
  "summarize_text",
  "Summarize text to a shorter version using extractive summarization.",
  {
    text: z.string().describe("Text to summarize"),
    max_sentences: z.number().optional().describe("Maximum sentences in summary (default 3)"),
  },
  async ({ text, max_sentences }) => {
    const result = await apiCall("/api/text/summarize", {
      method: "POST",
      body: JSON.stringify({ text, max_sentences: max_sentences || 3 }),
    });
    return textResult(result);
  }
);

server.tool(
  "detect_language",
  "Detect the language of a text string.",
  { text: z.string().describe("Text to detect language of") },
  async ({ text }) => {
    const result = await apiCall("/api/text/detect-language", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    return textResult(result);
  }
);

server.tool(
  "get_crypto_prices",
  "Get current cryptocurrency prices (BTC, ETH, SOL, etc.).",
  { coins: z.string().optional().describe("Comma-separated coin IDs (e.g., bitcoin,ethereum,solana)") },
  async ({ coins }) => {
    let url = "/api/crypto/prices";
    if (coins) url += `?coins=${encodeURIComponent(coins)}`;
    const result = await apiCall(url);
    return textResult(result);
  }
);

server.tool(
  "seo_analyze",
  "Analyze SEO metrics of a URL (title, meta, headers, links, performance).",
  { url: z.string().describe("URL to analyze for SEO") },
  async ({ url }) => {
    const result = await apiCall(`/seo/analyze?url=${encodeURIComponent(url)}`);
    return textResult(result);
  }
);

server.tool(
  "regex_test",
  "Test a regex pattern against text. Returns all matches, groups, and positions.",
  {
    pattern: z.string().describe("Regex pattern to test"),
    text: z.string().describe("Text to test against"),
    flags: z.string().optional().describe("Regex flags: i (case-insensitive), m (multiline), s (dotall)"),
  },
  async ({ pattern, text, flags }) => {
    const result = await apiCall("/api/regex/test", {
      method: "POST",
      body: JSON.stringify({ pattern, text, flags: flags || "" }),
    });
    return textResult(result);
  }
);

server.tool(
  "jwt_decode",
  "Decode a JWT token without verification. Shows header, payload, expiration.",
  { token: z.string().describe("JWT token to decode") },
  async ({ token }) => {
    const result = await apiCall("/api/jwt/decode", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
    return textResult(result);
  }
);

server.tool(
  "timestamp_convert",
  "Convert between Unix timestamps and human-readable dates, or get current time.",
  {
    timestamp: z.number().optional().describe("Unix timestamp to convert to date"),
    date_string: z.string().optional().describe("ISO date string to convert to timestamp"),
  },
  async ({ timestamp, date_string }) => {
    if (!timestamp && !date_string) {
      const result = await apiCall("/api/timestamp/now");
      return textResult(result);
    }
    const body = {};
    if (timestamp) body.timestamp = timestamp;
    if (date_string) body.date_string = date_string;
    const result = await apiCall("/api/timestamp/convert", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return textResult(result);
  }
);

server.tool(
  "text_diff",
  "Compare two texts and show differences (unified diff format).",
  {
    text1: z.string().describe("First text"),
    text2: z.string().describe("Second text"),
  },
  async ({ text1, text2 }) => {
    const result = await apiCall("/api/text/diff", {
      method: "POST",
      body: JSON.stringify({ text1, text2 }),
    });
    return textResult(result);
  }
);

server.tool(
  "cron_parse",
  "Parse a cron expression and explain it in plain English.",
  { expression: z.string().describe("Cron expression (5 or 6 fields)") },
  async ({ expression }) => {
    const result = await apiCall("/api/cron/parse", {
      method: "POST",
      body: JSON.stringify({ expression }),
    });
    return textResult(result);
  }
);

server.tool(
  "http_request",
  "Make an HTTP request and return response details (status, headers, body). Like curl via API.",
  {
    url: z.string().describe("URL to request"),
    method: z.string().optional().describe("HTTP method (GET, POST, PUT, DELETE)"),
    headers: z.record(z.string()).optional().describe("Request headers"),
    body: z.string().optional().describe("Request body"),
  },
  async ({ url, method, headers, body }) => {
    const result = await apiCall("/api/http/request", {
      method: "POST",
      body: JSON.stringify({ url, method: method || "GET", headers: headers || {}, body }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_password",
  "Generate secure random passwords with configurable options.",
  {
    length: z.number().optional().describe("Password length (default 16)"),
    count: z.number().optional().describe("Number of passwords (default 1)"),
    symbols: z.boolean().optional().describe("Include symbols (default true)"),
  },
  async ({ length, count, symbols }) => {
    const result = await apiCall("/api/password/generate", {
      method: "POST",
      body: JSON.stringify({ length: length || 16, count: count || 1, symbols: symbols !== false }),
    });
    return textResult(result);
  }
);

server.tool(
  "url_encode_decode",
  "URL encode or decode text.",
  {
    text: z.string().describe("Text to encode/decode"),
    action: z.string().optional().describe("'encode' or 'decode' (default encode)"),
  },
  async ({ text, action }) => {
    const result = await apiCall("/api/url/encode-decode", {
      method: "POST",
      body: JSON.stringify({ text, action: action || "encode" }),
    });
    return textResult(result);
  }
);

server.tool(
  "slugify",
  "Convert text to a URL-friendly slug.",
  { text: z.string().describe("Text to slugify") },
  async ({ text }) => {
    const result = await apiCall("/api/text/slugify", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    return textResult(result);
  }
);

server.tool(
  "markdown_table",
  "Generate a formatted markdown table from headers and rows.",
  {
    headers: z.array(z.string()).describe("Column headers"),
    rows: z.array(z.array(z.string())).describe("Table rows (array of arrays)"),
  },
  async ({ headers, rows }) => {
    const result = await apiCall("/api/markdown/table", {
      method: "POST",
      body: JSON.stringify({ headers, rows }),
    });
    return textResult(result);
  }
);

server.tool(
  "json_validate_schema",
  "Validate JSON data against a JSON Schema definition.",
  {
    data: z.string().describe("JSON data to validate"),
    schema_def: z.string().describe("JSON Schema definition"),
  },
  async ({ data, schema_def }) => {
    const result = await apiCall("/api/json/validate-schema", {
      method: "POST",
      body: JSON.stringify({ data, schema_def }),
    });
    return textResult(result);
  }
);

server.tool(
  "code_format",
  "Format/beautify code (supports JSON, SQL, HTML).",
  {
    code: z.string().describe("Code to format"),
    language: z.string().describe("Language: json, sql, html"),
  },
  async ({ code, language }) => {
    const result = await apiCall("/api/code/format", {
      method: "POST",
      body: JSON.stringify({ code, language }),
    });
    return textResult(result);
  }
);

// --- New Tools: AI Agent Utilities ---

server.tool(
  "generate_fake_data",
  "Generate fake/mock data for testing. Types: person, address, company, email, phone, credit_card, uuid, date, sentence, paragraph, product, url.",
  {
    type: z.string().describe("Data type: person, address, company, email, phone, credit_card, uuid, date, sentence, paragraph, product, url"),
    count: z.number().optional().describe("Number of items to generate (default 1, max 100)"),
  },
  async ({ type, count }) => {
    const result = await apiCall("/api/fake/generate", {
      method: "POST",
      body: JSON.stringify({ type, count: count || 1 }),
    });
    return textResult(result);
  }
);

server.tool(
  "json_query",
  "Query JSON data using dot-notation paths. Supports wildcards (*) and array indices.",
  {
    json_data: z.string().describe("JSON string to query"),
    path: z.string().describe("Dot-notation path (e.g., 'users[0].name', 'items.*.price')"),
  },
  async ({ json_data, path }) => {
    const result = await apiCall("/api/json/query", {
      method: "POST",
      body: JSON.stringify({ json_data, path }),
    });
    return textResult(result);
  }
);

server.tool(
  "json_to_schema",
  "Generate a JSON Schema from example JSON data. Useful for API docs and validation.",
  { json_data: z.string().describe("Example JSON to generate schema from") },
  async ({ json_data }) => {
    const result = await apiCall("/api/json/to-schema", {
      method: "POST",
      body: JSON.stringify({ json_data }),
    });
    return textResult(result);
  }
);

server.tool(
  "template_render",
  "Render a text template with variable substitution using {{variable}} syntax.",
  {
    template: z.string().describe("Template with {{variable}} placeholders"),
    variables: z.record(z.string()).describe("Key-value pairs for substitution"),
  },
  async ({ template, variables }) => {
    const result = await apiCall("/api/template/render", {
      method: "POST",
      body: JSON.stringify({ template, variables }),
    });
    return textResult(result);
  }
);

server.tool(
  "data_transform",
  "Apply transformations to JSON data. Operations: sort, filter, unique, reverse, flatten, group_by, limit, skip.",
  {
    data: z.string().describe("JSON array or object to transform"),
    operations: z.array(z.record(z.any())).describe("Array of operations: [{type:'sort',key:'name'}, {type:'filter',key:'age',operator:'gt',value:18}]"),
  },
  async ({ data, operations }) => {
    const result = await apiCall("/api/data/transform", {
      method: "POST",
      body: JSON.stringify({ data, operations }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_gitignore",
  "Generate a .gitignore file for specified languages/frameworks.",
  {
    languages: z.array(z.string()).describe("Languages: python, node, java, go, rust, ruby, swift, docker, general"),
    extras: z.array(z.string()).optional().describe("Additional custom patterns to ignore"),
  },
  async ({ languages, extras }) => {
    const result = await apiCall("/api/gitignore/generate", {
      method: "POST",
      body: JSON.stringify({ languages, extras: extras || [] }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_dockerfile",
  "Generate a Dockerfile for common language/framework combinations.",
  {
    language: z.string().describe("Language: python, node, go, rust, java"),
    framework: z.string().optional().describe("Framework: fastapi, flask, next, etc."),
    port: z.number().optional().describe("Port to expose (default 8080)"),
  },
  async ({ language, framework, port }) => {
    const result = await apiCall("/api/dockerfile/generate", {
      method: "POST",
      body: JSON.stringify({ language, framework: framework || "", port: port || 8080 }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_env_file",
  "Generate environment variable files in various formats (dotenv, docker, yaml, shell, json).",
  {
    variables: z.record(z.string()).describe("Key-value pairs for environment variables"),
    format: z.string().optional().describe("Output format: dotenv, docker, yaml, shell, json (default dotenv)"),
  },
  async ({ variables, format }) => {
    const result = await apiCall("/api/env/generate", {
      method: "POST",
      body: JSON.stringify({ variables, format: format || "dotenv" }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_openapi",
  "Generate an OpenAPI 3.0 spec from endpoint definitions.",
  {
    name: z.string().describe("API name"),
    description: z.string().optional().describe("API description"),
    endpoints: z.array(z.record(z.any())).describe("Array of {method, path, summary, request_body, response}"),
  },
  async ({ name, description, endpoints }) => {
    const result = await apiCall("/api/openapi/generate", {
      method: "POST",
      body: JSON.stringify({ name, description: description || "", endpoints }),
    });
    return textResult(result);
  }
);

server.tool(
  "validate_email",
  "Validate email address format and check domain MX records.",
  { email: z.string().describe("Email address to validate") },
  async ({ email }) => {
    const result = await apiCall("/api/validate/email", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    return textResult(result);
  }
);

server.tool(
  "validate_ip",
  "Validate and classify an IP address (IPv4/IPv6, private/public, etc.).",
  { ip: z.string().describe("IP address to validate") },
  async ({ ip }) => {
    const result = await apiCall("/api/validate/ip", {
      method: "POST",
      body: JSON.stringify({ ip }),
    });
    return textResult(result);
  }
);

server.tool(
  "csv_to_json",
  "Convert CSV text to JSON array.",
  { csv: z.string().describe("CSV text with headers") },
  async ({ csv }) => {
    const result = await apiCall("/api/convert/csv-to-json", {
      method: "POST",
      body: JSON.stringify({ csv }),
    });
    return textResult(result);
  }
);

server.tool(
  "yaml_to_json",
  "Convert YAML text to JSON.",
  { yaml: z.string().describe("YAML text to convert") },
  async ({ yaml }) => {
    const result = await apiCall("/api/convert/yaml-to-json", {
      method: "POST",
      body: JSON.stringify({ yaml }),
    });
    return textResult(result);
  }
);

server.tool(
  "json_diff",
  "Compare two JSON objects and return the differences.",
  {
    json1: z.string().describe("First JSON object"),
    json2: z.string().describe("Second JSON object"),
  },
  async ({ json1, json2 }) => {
    const result = await apiCall("/api/diff/json", {
      method: "POST",
      body: JSON.stringify({ json1, json2 }),
    });
    return textResult(result);
  }
);

server.tool(
  "lorem_ipsum",
  "Generate Lorem Ipsum placeholder text.",
  {
    paragraphs: z.number().optional().describe("Number of paragraphs (default 3)"),
    words_per_paragraph: z.number().optional().describe("Words per paragraph (default 50)"),
  },
  async ({ paragraphs, words_per_paragraph }) => {
    const result = await apiCall("/api/lorem-ipsum", {
      method: "POST",
      body: JSON.stringify({ paragraphs: paragraphs || 3, words_per_paragraph: words_per_paragraph || 50 }),
    });
    return textResult(result);
  }
);

server.tool(
  "html_encode_decode",
  "HTML entity encode or decode text.",
  {
    text: z.string().describe("Text to encode or decode"),
    action: z.string().optional().describe("'encode' or 'decode' (default encode)"),
  },
  async ({ text, action }) => {
    const result = await apiCall("/api/html/encode-decode", {
      method: "POST",
      body: JSON.stringify({ text, action: action || "encode" }),
    });
    return textResult(result);
  }
);

server.tool(
  "number_convert",
  "Convert numbers between decimal, binary, octal, hex, and roman numerals.",
  {
    value: z.string().describe("Number value to convert"),
    from: z.string().optional().describe("Source format: decimal, binary, octal, hex, roman (default decimal)"),
  },
  async ({ value, from: fromBase }) => {
    const result = await apiCall("/api/number/convert", {
      method: "POST",
      body: JSON.stringify({ value, from: fromBase || "decimal" }),
    });
    return textResult(result);
  }
);

// --- New High-Value Tools (v1.4.0) ---

server.tool(
  "web_extract",
  "Extract content from any web page: text, links, images, metadata, or structured data.",
  {
    url: z.string().describe("URL to extract content from"),
    extract: z.string().optional().describe("What to extract: text, links, images, metadata, structured (default: text)"),
  },
  async ({ url, extract }) => {
    const result = await apiCall("/api/web/extract", {
      method: "POST",
      body: JSON.stringify({ url, extract: extract || "text" }),
    });
    return textResult(result);
  }
);

server.tool(
  "code_analyze",
  "Analyze code: detect language, count lines, find functions/classes, measure complexity.",
  {
    code: z.string().describe("Source code to analyze"),
    language: z.string().optional().describe("Language hint (auto-detected if omitted)"),
  },
  async ({ code, language }) => {
    const result = await apiCall("/api/code/analyze", {
      method: "POST",
      body: JSON.stringify({ code, language: language || "auto" }),
    });
    return textResult(result);
  }
);

server.tool(
  "schema_generate",
  "Generate type definitions from JSON. Supports TypeScript, Python (Pydantic), Zod, JSON Schema.",
  {
    data: z.string().describe("JSON data to generate schema from"),
    format: z.string().optional().describe("Output format: typescript, python, zod, jsonschema (default: typescript)"),
  },
  async ({ data, format }) => {
    const result = await apiCall("/api/schema/generate", {
      method: "POST",
      body: JSON.stringify({ data, format: format || "typescript" }),
    });
    return textResult(result);
  }
);

server.tool(
  "prompt_build",
  "Build structured LLM prompts with variable substitution and system/user message formatting.",
  {
    template: z.string().describe("Prompt template with {{variable}} placeholders"),
    variables: z.record(z.string()).optional().describe("Variables to substitute into template"),
    system: z.string().optional().describe("System message template"),
  },
  async ({ template, variables, system }) => {
    const result = await apiCall("/api/prompt/build", {
      method: "POST",
      body: JSON.stringify({ template, variables: variables || {}, system: system || "" }),
    });
    return textResult(result);
  }
);

server.tool(
  "test_endpoint",
  "Test any API endpoint: send requests and get detailed response metrics, timing, and body.",
  {
    url: z.string().describe("URL to test"),
    method: z.string().optional().describe("HTTP method (default: GET)"),
    headers: z.record(z.string()).optional().describe("Request headers"),
    body: z.string().optional().describe("Request body (for POST/PUT)"),
  },
  async ({ url, method, headers, body }) => {
    const result = await apiCall("/api/test/endpoint", {
      method: "POST",
      body: JSON.stringify({ url, method: method || "GET", headers: headers || {}, body: body || "" }),
    });
    return textResult(result);
  }
);

server.tool(
  "text_similarity",
  "Calculate text similarity using Jaccard, cosine, and character-level algorithms.",
  {
    text1: z.string().describe("First text"),
    text2: z.string().describe("Second text"),
  },
  async ({ text1, text2 }) => {
    const result = await apiCall("/api/text/similarity", {
      method: "POST",
      body: JSON.stringify({ text1, text2 }),
    });
    return textResult(result);
  }
);

// --- New Tools: IP Lookup, Cron Parser, Text Diff, JWT Decode, Time Convert, etc. ---

server.tool(
  "ip_lookup",
  "Look up geolocation, ISP, and network info for any IP address.",
  {
    ip: z.string().describe("IP address to look up"),
  },
  async ({ ip }) => {
    const result = await apiCall(`/api/ip/lookup?ip=${encodeURIComponent(ip)}`);
    return textResult(result);
  }
);

server.tool(
  "cron_parse",
  "Parse and explain a cron expression, show next N scheduled run times.",
  {
    expression: z.string().describe("Cron expression (e.g., '*/5 * * * *')"),
    count: z.number().optional().describe("Number of next runs to show (default: 5)"),
  },
  async ({ expression, count }) => {
    const result = await apiCall(`/api/cron/parse?expression=${encodeURIComponent(expression)}&count=${count || 5}`);
    return textResult(result);
  }
);

server.tool(
  "text_diff",
  "Generate a unified diff between two text inputs.",
  {
    original: z.string().describe("Original text"),
    modified: z.string().describe("Modified text"),
    context_lines: z.number().optional().describe("Lines of context (default: 3)"),
  },
  async ({ original, modified, context_lines }) => {
    const result = await apiCall("/api/diff/text", {
      method: "POST",
      body: JSON.stringify({ original, modified, context_lines: context_lines || 3 }),
    });
    return textResult(result);
  }
);

server.tool(
  "jwt_decode",
  "Decode a JWT token without verification. Inspect header, payload, and expiration.",
  {
    token: z.string().describe("JWT token to decode"),
  },
  async ({ token }) => {
    const result = await apiCall("/api/jwt/decode", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
    return textResult(result);
  }
);

server.tool(
  "time_convert",
  "Convert between Unix timestamps, ISO 8601, and human-readable date formats.",
  {
    timestamp: z.string().optional().describe("Timestamp to convert (Unix seconds/ms, ISO 8601, or date string). Empty = current time."),
  },
  async ({ timestamp }) => {
    const url = timestamp ? `/api/time/convert?timestamp=${encodeURIComponent(timestamp)}` : "/api/time/convert";
    const result = await apiCall(url);
    return textResult(result);
  }
);

server.tool(
  "headers_analyze",
  "Analyze HTTP response headers of any URL for security, caching, and configuration.",
  {
    url: z.string().describe("URL to analyze"),
  },
  async ({ url }) => {
    const result = await apiCall(`/api/headers/analyze?url=${encodeURIComponent(url)}`);
    return textResult(result);
  }
);

server.tool(
  "password_check",
  "Check password strength and get improvement suggestions.",
  {
    password: z.string().describe("Password to check"),
  },
  async ({ password }) => {
    const result = await apiCall("/api/password/check", {
      method: "POST",
      body: JSON.stringify({ password }),
    });
    return textResult(result);
  }
);

server.tool(
  "regex_test",
  "Test a regex pattern against text. Returns all matches with positions and groups.",
  {
    pattern: z.string().describe("Regex pattern"),
    text: z.string().describe("Text to test against"),
    flags: z.string().optional().describe("Flags: i=case-insensitive, m=multiline, s=dotall"),
  },
  async ({ pattern, text, flags }) => {
    const result = await apiCall("/api/regex/test", {
      method: "POST",
      body: JSON.stringify({ pattern, text, flags: flags || "" }),
    });
    return textResult(result);
  }
);

server.tool(
  "lorem_ipsum",
  "Generate lorem ipsum placeholder text.",
  {
    paragraphs: z.number().optional().describe("Number of paragraphs (default: 3)"),
    format: z.string().optional().describe("Output format: text or html (default: text)"),
  },
  async ({ paragraphs, format }) => {
    const params = new URLSearchParams();
    if (paragraphs) params.set("paragraphs", String(paragraphs));
    if (format) params.set("format", format);
    const result = await apiCall(`/api/lorem?${params.toString()}`);
    return textResult(result);
  }
);

server.tool(
  "color_palette",
  "Generate color palettes (complementary, analogous, triadic, monochromatic) from a base color.",
  {
    base_color: z.string().describe("Base hex color (e.g., #3498db)"),
    scheme: z.string().optional().describe("Scheme: complementary, analogous, triadic, monochromatic (default: complementary)"),
    count: z.number().optional().describe("Number of colors (default: 5)"),
  },
  async ({ base_color, scheme, count }) => {
    const params = new URLSearchParams({ base_color });
    if (scheme) params.set("scheme", scheme);
    if (count) params.set("count", String(count));
    const result = await apiCall(`/api/color/palette?${params.toString()}`);
    return textResult(result);
  }
);

server.tool(
  "slug_generate",
  "Generate URL-friendly slugs from text.",
  {
    text: z.string().describe("Text to convert to a slug"),
    separator: z.string().optional().describe("Separator character (default: -)"),
  },
  async ({ text, separator }) => {
    const result = await apiCall("/api/slug/generate", {
      method: "POST",
      body: JSON.stringify({ text, separator: separator || "-" }),
    });
    return textResult(result);
  }
);

server.tool(
  "markdown_strip",
  "Strip markdown formatting and return plain text.",
  {
    markdown: z.string().describe("Markdown text to strip"),
  },
  async ({ markdown }) => {
    const result = await apiCall("/api/markdown/strip", {
      method: "POST",
      body: JSON.stringify({ markdown }),
    });
    return textResult(result);
  }
);

// --- AI Agent Utility Tools ---

server.tool(
  "extract_structured",
  "Extract structured data (emails, URLs, phones, dates, numbers, addresses) from unstructured text.",
  {
    text: z.string().describe("Text to extract data from"),
    extract: z.enum(["entities", "emails", "urls", "phones", "dates", "numbers", "addresses", "all"]).optional().describe("Type of data to extract (default: entities)"),
  },
  async ({ text, extract }) => {
    const result = await apiCall("/api/extract/structured", {
      method: "POST",
      body: JSON.stringify({ text, extract: extract || "all" }),
    });
    return textResult(result);
  }
);

server.tool(
  "text_transform",
  "Apply text transformations: uppercase, lowercase, title, reverse, sort_lines, unique_lines, trim, number_lines, remove_blank_lines, remove_duplicates.",
  {
    text: z.string().describe("Text to transform"),
    transforms: z.array(z.string()).describe("List of transforms to apply in order"),
  },
  async ({ text, transforms }) => {
    const result = await apiCall("/api/text/transform", {
      method: "POST",
      body: JSON.stringify({ text, transforms }),
    });
    return textResult(result);
  }
);

server.tool(
  "text_compare",
  "Compare multiple text strings for similarity using Levenshtein distance.",
  {
    items: z.array(z.string()).describe("List of strings to compare (2-20)"),
  },
  async ({ items }) => {
    const result = await apiCall("/api/text/compare", {
      method: "POST",
      body: JSON.stringify({ items }),
    });
    return textResult(result);
  }
);

server.tool(
  "convert_units",
  "Convert between units: length (m,ft,km,mi), weight (kg,lb), temperature (c,f,k), volume (l,gal), speed (mph,kph), data (kb,mb,gb).",
  {
    value: z.number().describe("Value to convert"),
    from_unit: z.string().describe("Source unit"),
    to_unit: z.string().describe("Target unit"),
  },
  async ({ value, from_unit, to_unit }) => {
    const result = await apiCall("/api/convert/units", {
      method: "POST",
      body: JSON.stringify({ value, from_unit, to_unit }),
    });
    return textResult(result);
  }
);

// --- API Key & Payment Management (for AI agent self-service) ---

server.tool(
  "register_api_key",
  "Register a free API key for ToolPipe (100 calls/day). Returns the API key immediately.",
  {
    email: z.string().email().describe("Email address for the API key"),
  },
  async ({ email }) => {
    const result = await apiCall("/api-keys/register", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    return textResult(result);
  }
);

server.tool(
  "check_api_usage",
  "Check API key usage, remaining quota, and tier info. Use to monitor consumption.",
  {
    api_key: z.string().optional().describe("API key to check (or use email)"),
    email: z.string().optional().describe("Email to look up (or use api_key)"),
  },
  async ({ api_key, email }) => {
    const params = new URLSearchParams();
    if (api_key) params.set("api_key", api_key);
    if (email) params.set("email", email);
    const result = await apiCall(`/api-keys/usage?${params.toString()}`);
    return textResult(result);
  }
);

server.tool(
  "create_payment",
  "Create a crypto payment order to upgrade API key to Pro ($9.99/mo) or Enterprise ($49.99/mo).",
  {
    email: z.string().email().describe("Email associated with the API key"),
    tier: z.enum(["pro", "enterprise"]).describe("Plan tier to purchase"),
  },
  async ({ email, tier }) => {
    const result = await apiCall("/payments/create", {
      method: "POST",
      body: JSON.stringify({ email, tier }),
    });
    return textResult(result);
  }
);

server.tool(
  "verify_payment",
  "Verify a crypto payment on-chain using transaction hash. Automatically upgrades the API key.",
  {
    order_id: z.string().describe("Order ID from create_payment"),
    tx_hash: z.string().describe("Transaction hash (0x + 64 hex chars)"),
  },
  async ({ order_id, tx_hash }) => {
    const result = await apiCall("/payments/verify-tx", {
      method: "POST",
      body: JSON.stringify({ order_id, tx_hash }),
    });
    return textResult(result);
  }
);

server.tool(
  "get_pricing",
  "Get ToolPipe API pricing information and available tiers.",
  {},
  async () => {
    const result = await apiCall("/api/pricing");
    return textResult(result);
  }
);

server.tool(
  "agent_pay",
  "Agent-optimized payment: get crypto payment instructions to upgrade API key. Returns wallet addresses, supported tokens/chains, and verification instructions. Recommended: USDC on Base (lowest fees).",
  {
    email: z.string().describe("Email for API key"),
    tier: z.enum(["pro", "enterprise"]).optional().describe("Plan tier: pro ($9.99/mo) or enterprise ($49.99/mo)"),
    preferred_chain: z.enum(["base", "polygon", "arbitrum", "ethereum", "optimism", "solana"]).optional().describe("Preferred blockchain (default: base)"),
  },
  async ({ email, tier, preferred_chain }) => {
    const result = await apiCall("/payments/agent-pay", {
      method: "POST",
      body: JSON.stringify({ email, tier: tier ?? "pro", preferred_chain: preferred_chain ?? "base" }),
    });
    return textResult(result);
  }
);

// --- New Tools: Batch 3 (session 17) ---

server.tool(
  "sql_format",
  "Format and prettify SQL queries with proper indentation and keyword casing.",
  {
    sql: z.string().describe("SQL query to format"),
    uppercase_keywords: z.boolean().optional().describe("Uppercase SQL keywords (default true)"),
  },
  async ({ sql, uppercase_keywords }) => {
    const result = await apiCall("/api/sql/format", {
      method: "POST",
      body: JSON.stringify({ sql, uppercase_keywords: uppercase_keywords ?? true }),
    });
    return textResult(result);
  }
);

server.tool(
  "html_strip",
  "Strip HTML tags and return plain text. Optionally preserve link URLs.",
  {
    html: z.string().describe("HTML content to strip"),
    preserve_links: z.boolean().optional().describe("Keep link URLs in output (default false)"),
  },
  async ({ html, preserve_links }) => {
    const result = await apiCall("/api/html/strip", {
      method: "POST",
      body: JSON.stringify({ html, preserve_links: preserve_links ?? false }),
    });
    return textResult(result);
  }
);

server.tool(
  "text_stats",
  "Get detailed text statistics: word count, char count, reading time, readability scores.",
  {
    text: z.string().describe("Text to analyze"),
  },
  async ({ text }) => {
    const result = await apiCall("/api/text/stats", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    return textResult(result);
  }
);

server.tool(
  "number_format",
  "Format numbers: comma-separated, words, roman numerals, scientific, binary, hex, octal.",
  {
    number: z.number().describe("Number to format"),
    format: z.string().optional().describe("Format: comma, words, roman, scientific, binary, hex, octal, all (default: all)"),
  },
  async ({ number, format }) => {
    const result = await apiCall("/api/number/format", {
      method: "POST",
      body: JSON.stringify({ number, format: format ?? "all" }),
    });
    return textResult(result);
  }
);

server.tool(
  "xml_to_json",
  "Convert XML to JSON.",
  {
    xml: z.string().describe("XML content to convert"),
  },
  async ({ xml }) => {
    const result = await apiCall("/api/xml/to-json", {
      method: "POST",
      body: JSON.stringify({ xml }),
    });
    return textResult(result);
  }
);

server.tool(
  "yaml_validate",
  "Validate YAML syntax and convert to JSON.",
  {
    yaml_text: z.string().describe("YAML content to validate"),
  },
  async ({ yaml_text }) => {
    const result = await apiCall("/api/yaml/validate", {
      method: "POST",
      body: JSON.stringify({ yaml_text }),
    });
    return textResult(result);
  }
);

server.tool(
  "env_parse",
  "Parse .env file content to JSON. Handles comments, quotes.",
  {
    env_text: z.string().describe(".env file content to parse"),
  },
  async ({ env_text }) => {
    const result = await apiCall("/api/env/parse", {
      method: "POST",
      body: JSON.stringify({ env_text }),
    });
    return textResult(result);
  }
);

server.tool(
  "http_status",
  "Get information about an HTTP status code.",
  {
    code: z.number().describe("HTTP status code (e.g., 200, 404, 500)"),
  },
  async ({ code }) => {
    const result = await apiCall(`/api/http-status/${code}`);
    return textResult(result);
  }
);

server.tool(
  "jwt_create",
  "Create a JWT token from a payload (for testing/development).",
  {
    payload: z.string().describe("JSON string of the JWT payload"),
    secret: z.string().optional().describe("Secret key for signing (default: your-secret-key)"),
  },
  async ({ payload, secret }) => {
    const result = await apiCall("/api/jwt/create", {
      method: "POST",
      body: JSON.stringify({ payload: JSON.parse(payload), secret: secret ?? "your-secret-key" }),
    });
    return textResult(result);
  }
);

server.tool(
  "my_ip",
  "Get the caller's IP address and request info.",
  {},
  async () => {
    const result = await apiCall("/api/myip");
    return textResult(result);
  }
);

// --- Webhook Tester ---

server.tool(
  "webhook_create",
  "Create a webhook bin for testing. Send requests to /webhooks/{bin_id} and inspect them.",
  {},
  async () => {
    const result = await apiCall("/api/webhooks/create", { method: "POST" });
    return textResult(result);
  }
);

server.tool(
  "webhook_inspect",
  "Inspect captured webhook requests for a bin.",
  {
    bin_id: z.string().describe("The webhook bin ID"),
    limit: z.number().optional().describe("Max requests to return (default 20)"),
  },
  async ({ bin_id, limit }) => {
    const params = limit ? `?limit=${limit}` : "";
    const result = await apiCall(`/api/webhooks/${bin_id}/requests${params}`);
    return textResult(result);
  }
);

// --- Mock Data Generator ---

server.tool(
  "mock_generate",
  "Generate mock API data. Templates: user, product, order, comment, post. Or provide a custom schema.",
  {
    template: z.string().optional().describe("Template name: user, product, order, comment, post"),
    count: z.number().optional().describe("Number of items to generate (max 100)"),
    schema: z.string().optional().describe("Custom schema as JSON: {\"name\": \"name\", \"age\": \"int\", \"email\": \"email\"}"),
    format: z.string().optional().describe("Output format: json (default), csv"),
  },
  async ({ template, count, schema, format }) => {
    const body = { template, count: count ?? 1, format: format ?? "json" };
    if (schema) body.schema = JSON.parse(schema);
    const result = await apiCall("/api/mock/generate", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return textResult(result);
  }
);

// --- Crontab Generator ---

server.tool(
  "crontab_generate",
  "Generate a cron expression from plain English. e.g. 'every 5 minutes', 'daily at 3am', 'weekdays at noon'.",
  {
    description: z.string().describe("Plain English schedule description"),
  },
  async ({ description }) => {
    const result = await apiCall("/api/crontab/generate", {
      method: "POST",
      body: JSON.stringify({ description }),
    });
    return textResult(result);
  }
);

// --- Diff Generator ---

server.tool(
  "diff_generate",
  "Generate a diff/patch between two texts. Supports unified, context, and HTML formats.",
  {
    original: z.string().describe("Original text"),
    modified: z.string().describe("Modified text"),
    format: z.string().optional().describe("Diff format: unified (default), context, html"),
  },
  async ({ original, modified, format }) => {
    const result = await apiCall("/api/diff/generate", {
      method: "POST",
      body: JSON.stringify({ original, modified, format: format ?? "unified" }),
    });
    return textResult(result);
  }
);

// --- API Stats ---

server.tool(
  "api_stats",
  "Get ToolPipe API statistics: endpoints, tools, pricing, payment methods.",
  {},
  async () => {
    const result = await apiCall("/api/stats");
    return textResult(result);
  }
);

// --- Placeholder Image ---

server.tool(
  "placeholder_image",
  "Generate a placeholder image URL. Returns a URL you can use in HTML/Markdown. Supports custom size, colors, and text.",
  {
    width: z.number().describe("Image width in pixels (1-4000)"),
    height: z.number().optional().describe("Image height in pixels (defaults to width)"),
    bg: z.string().optional().describe("Background color hex (default: cccccc)"),
    fg: z.string().optional().describe("Text color hex (default: 333333)"),
    text: z.string().optional().describe("Custom text on the image"),
  },
  async ({ width, height, bg, fg, text }) => {
    const h = height ?? width;
    const params = new URLSearchParams();
    if (bg) params.set("bg", bg);
    if (fg) params.set("fg", fg);
    if (text) params.set("text", text);
    const qs = params.toString() ? "?" + params.toString() : "";
    const url = `${BASE_URL}/api/placeholder/${width}x${h}${qs}`;
    return textResult({ url, width, height: h, usage: `<img src="${url}" alt="placeholder">` });
  }
);

// --- Favicon Extractor ---

server.tool(
  "favicon_extract",
  "Extract favicon URL(s) from any website. Returns all found favicons and a Google proxy fallback.",
  {
    url: z.string().describe("Website URL to extract favicon from (e.g. github.com)"),
  },
  async ({ url }) => {
    const result = await apiCall(`/api/favicon?url=${encodeURIComponent(url)}`);
    return textResult(result);
  }
);

// --- Sitemap Generator ---

server.tool(
  "sitemap_generate",
  "Generate an XML sitemap from a list of URLs. Returns valid sitemap XML.",
  {
    base_url: z.string().describe("Base URL of the website (e.g. https://example.com)"),
    urls: z.array(z.string()).describe("Array of URL paths (e.g. ['/', '/about', '/pricing'])"),
    changefreq: z.string().optional().describe("Change frequency: always, hourly, daily, weekly, monthly, yearly, never"),
  },
  async ({ base_url, urls, changefreq }) => {
    const result = await apiCall("/api/sitemap/generate", {
      method: "POST",
      body: JSON.stringify({ base_url, urls, changefreq: changefreq ?? "weekly" }),
    });
    return textResult(result);
  }
);

// --- README Generator ---

server.tool(
  "readme_generate",
  "Generate a README.md file from project metadata. Returns formatted Markdown.",
  {
    name: z.string().describe("Project name"),
    description: z.string().optional().describe("Project description"),
    features: z.array(z.string()).optional().describe("List of features"),
    install: z.string().optional().describe("Installation command"),
    usage: z.string().optional().describe("Usage example"),
    license: z.string().optional().describe("License name (default: MIT)"),
    tech_stack: z.array(z.string()).optional().describe("Technologies used"),
  },
  async ({ name, description, features, install, usage, license, tech_stack }) => {
    const result = await apiCall("/api/readme/generate", {
      method: "POST",
      body: JSON.stringify({ name, description, features, install, usage, license, tech_stack }),
    });
    return textResult(result);
  }
);

// --- CSS Gradient Generator ---

server.tool(
  "css_gradient",
  "Generate CSS gradient code from colors. Returns CSS property and preview SVG.",
  {
    colors: z.string().describe("Comma-separated hex colors (e.g. 'ff0000,00ff00,0000ff')"),
    direction: z.string().optional().describe("Gradient direction (e.g. '135deg', 'to right')"),
    type: z.string().optional().describe("Gradient type: linear or radial"),
  },
  async ({ colors, direction, type }) => {
    const params = new URLSearchParams({ colors });
    if (direction) params.set("direction", direction);
    if (type) params.set("type", type);
    const result = await apiCall(`/api/gradient?${params.toString()}`);
    return textResult(result);
  }
);

// --- Meta Tags Generator ---

server.tool(
  "metatags_generate",
  "Generate Open Graph and Twitter Card meta tags for a webpage.",
  {
    title: z.string().describe("Page title"),
    description: z.string().optional().describe("Page description"),
    url: z.string().optional().describe("Page URL"),
    image: z.string().optional().describe("OG image URL"),
    site_name: z.string().optional().describe("Site name"),
    twitter_handle: z.string().optional().describe("Twitter handle (e.g. @example)"),
  },
  async ({ title, description, url, image, site_name, twitter_handle }) => {
    const result = await apiCall("/api/metatags/generate", {
      method: "POST",
      body: JSON.stringify({ title, description, url, image, site_name, twitter_handle }),
    });
    return textResult(result);
  }
);

// --- Robots.txt Generator ---

server.tool(
  "robots_generate",
  "Generate a robots.txt file from rules.",
  {
    rules: z.array(z.object({
      user_agent: z.string().describe("User agent (e.g. '*', 'Googlebot')"),
      allow: z.array(z.string()).optional().describe("Allowed paths"),
      disallow: z.array(z.string()).optional().describe("Disallowed paths"),
    })).optional().describe("Robots rules"),
    sitemap: z.string().optional().describe("Sitemap URL"),
  },
  async ({ rules, sitemap }) => {
    const result = await apiCall("/api/robots/generate", {
      method: "POST",
      body: JSON.stringify({ rules, sitemap }),
    });
    return textResult(result);
  }
);

// --- Htaccess Generator ---

server.tool(
  "htaccess_generate",
  "Generate Apache .htaccess rules for redirects, HTTPS, caching, and more.",
  {
    force_https: z.boolean().optional().describe("Force HTTPS redirect (default: true)"),
    www_redirect: z.string().optional().describe("WWW redirect: to_www, to_non_www, or none"),
    gzip: z.boolean().optional().describe("Enable gzip compression (default: true)"),
    cache_static: z.boolean().optional().describe("Cache static files (default: true)"),
  },
  async ({ force_https, www_redirect, gzip, cache_static }) => {
    const result = await apiCall("/api/htaccess/generate", {
      method: "POST",
      body: JSON.stringify({ force_https, www_redirect, gzip, cache_static }),
    });
    return textResult(result);
  }
);

// --- Text Processing Tools ---

server.tool(
  "text_summarize",
  "Summarize text using extractive summarization. Returns key sentences.",
  {
    text: z.string().describe("Text to summarize"),
    max_sentences: z.number().optional().describe("Max sentences in summary (default: 3)"),
  },
  async ({ text, max_sentences }) => {
    const result = await apiCall("/api/text/summarize", {
      method: "POST",
      body: JSON.stringify({ text, max_sentences }),
    });
    return textResult(result);
  }
);

server.tool(
  "text_keywords",
  "Extract keywords from text with relevance scoring.",
  {
    text: z.string().describe("Text to extract keywords from"),
    top_n: z.number().optional().describe("Number of keywords to return (default: 10)"),
  },
  async ({ text, top_n }) => {
    const result = await apiCall("/api/text/keywords", {
      method: "POST",
      body: JSON.stringify({ text, top_n }),
    });
    return textResult(result);
  }
);

server.tool(
  "text_readability",
  "Calculate readability scores (Flesch-Kincaid, Coleman-Liau, ARI).",
  {
    text: z.string().describe("Text to analyze for readability"),
  },
  async ({ text }) => {
    const result = await apiCall("/api/text/readability", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    return textResult(result);
  }
);

// --- Data Transform Tools ---

server.tool(
  "json_to_csv",
  "Convert a JSON array of objects to CSV format.",
  {
    data: z.array(z.record(z.any())).describe("Array of objects to convert"),
    delimiter: z.string().optional().describe("CSV delimiter (default: comma)"),
  },
  async ({ data, delimiter }) => {
    const result = await apiCall("/api/transform/json-to-csv", {
      method: "POST",
      body: JSON.stringify({ data, delimiter }),
    });
    return textResult(result);
  }
);

server.tool(
  "csv_to_json",
  "Convert CSV text to a JSON array of objects.",
  {
    csv: z.string().describe("CSV text to convert"),
    delimiter: z.string().optional().describe("CSV delimiter (default: comma)"),
  },
  async ({ csv, delimiter }) => {
    const result = await apiCall("/api/transform/csv-to-json", {
      method: "POST",
      body: JSON.stringify({ csv, delimiter }),
    });
    return textResult(result);
  }
);

server.tool(
  "xml_to_json",
  "Convert XML text to JSON.",
  {
    xml: z.string().describe("XML text to convert"),
  },
  async ({ xml }) => {
    const result = await apiCall("/api/transform/xml-to-json", {
      method: "POST",
      body: JSON.stringify({ xml }),
    });
    return textResult(result);
  }
);

// --- Code Generation Tools ---

server.tool(
  "generate_typescript_interface",
  "Generate TypeScript interface/type from a JSON object or array.",
  {
    data: z.any().describe("JSON data to generate TypeScript interface from"),
    name: z.string().optional().describe("Interface name (default: Generated)"),
  },
  async ({ data, name }) => {
    const result = await apiCall("/api/generate/typescript-interface", {
      method: "POST",
      body: JSON.stringify({ data, name }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_sql_create",
  "Generate SQL CREATE TABLE from column definitions or sample data.",
  {
    table: z.string().optional().describe("Table name"),
    data: z.any().optional().describe("Sample JSON data to infer columns from"),
    columns: z.array(z.object({
      name: z.string(),
      type: z.string(),
      nullable: z.boolean().optional(),
      primary_key: z.boolean().optional(),
    })).optional().describe("Column definitions"),
    dialect: z.string().optional().describe("SQL dialect (postgresql, mysql, sqlite)"),
  },
  async ({ table, data, columns, dialect }) => {
    const result = await apiCall("/api/generate/sql-create", {
      method: "POST",
      body: JSON.stringify({ table, data, columns, dialect }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_github_actions",
  "Generate a GitHub Actions CI/CD workflow YAML.",
  {
    name: z.string().optional().describe("Workflow name (default: CI)"),
    language: z.string().optional().describe("Language: node, python, etc."),
    trigger: z.string().optional().describe("Trigger event (default: push)"),
  },
  async ({ name, language, trigger }) => {
    const result = await apiCall("/api/generate/github-actions", {
      method: "POST",
      body: JSON.stringify({ name, language, trigger }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_nginx_config",
  "Generate an Nginx server configuration with SSL and proxy settings.",
  {
    domain: z.string().optional().describe("Domain name"),
    upstream_port: z.number().optional().describe("Upstream port (default: 3000)"),
    ssl: z.boolean().optional().describe("Enable SSL (default: true)"),
  },
  async ({ domain, upstream_port, ssl }) => {
    const result = await apiCall("/api/generate/nginx-config", {
      method: "POST",
      body: JSON.stringify({ domain, upstream_port, ssl }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_docker_compose",
  "Generate a docker-compose.yml from service definitions.",
  {
    services: z.array(z.object({
      name: z.string().describe("Service name"),
      image: z.string().optional().describe("Docker image"),
      ports: z.array(z.string()).optional().describe("Port mappings"),
      environment: z.record(z.string()).optional().describe("Environment variables"),
    })).describe("Service definitions"),
  },
  async ({ services }) => {
    const result = await apiCall("/api/generate/docker-compose", {
      method: "POST",
      body: JSON.stringify({ services }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_package_json",
  "Generate a package.json from project metadata.",
  {
    name: z.string().optional().describe("Package name"),
    description: z.string().optional().describe("Package description"),
    dependencies: z.record(z.string()).optional().describe("Dependencies"),
  },
  async ({ name, description, dependencies }) => {
    const result = await apiCall("/api/generate/package-json", {
      method: "POST",
      body: JSON.stringify({ name, description, dependencies }),
    });
    return textResult(result);
  }
);

// --- Security Tools ---

server.tool(
  "csp_generate",
  "Generate Content Security Policy headers from rules.",
  {
    directives: z.record(z.array(z.string())).optional().describe("CSP directives"),
    report_only: z.boolean().optional().describe("Report-only mode"),
  },
  async ({ directives, report_only }) => {
    const result = await apiCall("/api/security/csp-generate", {
      method: "POST",
      body: JSON.stringify({ directives, report_only }),
    });
    return textResult(result);
  }
);

server.tool(
  "cors_headers",
  "Generate CORS headers configuration with Nginx example.",
  {
    origins: z.array(z.string()).optional().describe("Allowed origins"),
    methods: z.array(z.string()).optional().describe("Allowed methods"),
    credentials: z.boolean().optional().describe("Allow credentials"),
  },
  async ({ origins, methods, credentials }) => {
    const result = await apiCall("/api/security/cors-headers", {
      method: "POST",
      body: JSON.stringify({ origins, methods, credentials }),
    });
    return textResult(result);
  }
);

// --- Network Tools ---

server.tool(
  "ssl_check",
  "Check SSL certificate details for a domain.",
  {
    domain: z.string().describe("Domain name to check SSL certificate for"),
  },
  async ({ domain }) => {
    const result = await apiCall(`/api/ssl/check?domain=${encodeURIComponent(domain)}`);
    return textResult(result);
  }
);

server.tool(
  "whois_lookup",
  "WHOIS lookup for a domain.",
  {
    domain: z.string().describe("Domain to look up"),
  },
  async ({ domain }) => {
    const result = await apiCall(`/api/whois?domain=${encodeURIComponent(domain)}`);
    return textResult(result);
  }
);

server.tool(
  "http_headers",
  "Fetch HTTP response headers from a URL.",
  {
    url: z.string().describe("URL to fetch headers from"),
  },
  async ({ url }) => {
    const result = await apiCall(`/api/headers/get?url=${encodeURIComponent(url)}`);
    return textResult(result);
  }
);

// --- Encoding Tools ---

server.tool(
  "url_encode",
  "URL-encode a string.",
  { text: z.string().describe("Text to URL-encode") },
  async ({ text }) => {
    const result = await apiCall(`/api/encode/url?text=${encodeURIComponent(text)}`);
    return textResult(result);
  }
);

server.tool(
  "url_decode",
  "URL-decode a string.",
  { text: z.string().describe("Text to URL-decode") },
  async ({ text }) => {
    const result = await apiCall(`/api/decode/url?text=${encodeURIComponent(text)}`);
    return textResult(result);
  }
);

server.tool(
  "html_encode",
  "HTML-encode a string (escape special characters).",
  { text: z.string().describe("Text to HTML-encode") },
  async ({ text }) => {
    const result = await apiCall(`/api/encode/html?text=${encodeURIComponent(text)}`);
    return textResult(result);
  }
);

server.tool(
  "html_decode",
  "HTML-decode a string (unescape entities).",
  { text: z.string().describe("Text to HTML-decode") },
  async ({ text }) => {
    const result = await apiCall(`/api/decode/html?text=${encodeURIComponent(text)}`);
    return textResult(result);
  }
);

server.tool(
  "hash_multiple",
  "Generate MD5, SHA1, SHA256, SHA512, BLAKE2b, BLAKE2s hashes for text.",
  { text: z.string().describe("Text to hash") },
  async ({ text }) => {
    const result = await apiCall(`/api/hash/file?text=${encodeURIComponent(text)}`);
    return textResult(result);
  }
);

// --- Utility Tools ---

server.tool(
  "timestamp",
  "Get current timestamp or convert Unix timestamp to multiple formats.",
  { ts: z.number().optional().describe("Unix timestamp to convert (omit for current time)") },
  async ({ ts }) => {
    const url = ts != null ? `/api/timestamp?ts=${ts}` : "/api/timestamp";
    const result = await apiCall(url);
    return textResult(result);
  }
);

server.tool(
  "text_diff_detailed",
  "Detailed text diff with line-by-line additions and deletions.",
  {
    text1: z.string().describe("Original text"),
    text2: z.string().describe("Modified text"),
  },
  async ({ text1, text2 }) => {
    const result = await apiCall("/api/diff/text-detailed", {
      method: "POST",
      body: JSON.stringify({ text1, text2 }),
    });
    return textResult(result);
  }
);

// --- Premium Tools (v1.13.0) ---

server.tool(
  "code_review",
  "Analyze code for bugs, security issues, and improvements. Returns a score, grade, and list of issues.",
  {
    code: z.string().describe("Source code to review"),
    language: z.string().optional().default("auto").describe("Language: python, javascript, go, rust, java, or auto"),
  },
  async ({ code, language }) => {
    const result = await apiCall("/api/code/review", {
      method: "POST",
      body: JSON.stringify({ code, language }),
    });
    return textResult(result);
  }
);

server.tool(
  "code_explain",
  "Generate a plain-English explanation of code, including function signatures and structure.",
  {
    code: z.string().describe("Source code to explain"),
  },
  async ({ code }) => {
    const result = await apiCall("/api/code/explain", {
      method: "POST",
      body: JSON.stringify({ code }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_openapi_spec",
  "Generate an OpenAPI 3.0 spec (JSON + YAML) from endpoint definitions.",
  {
    title: z.string().describe("API title"),
    version: z.string().optional().default("1.0.0"),
    description: z.string().optional().default(""),
    base_url: z.string().optional().default("https://api.example.com"),
    endpoints: z.array(z.object({
      path: z.string(),
      method: z.string().optional().default("get"),
      summary: z.string().optional().default(""),
    })).describe("Array of endpoint definitions"),
  },
  async ({ title, version, description, base_url, endpoints }) => {
    const result = await apiCall("/api/openapi/generate", {
      method: "POST",
      body: JSON.stringify({ title, version, description, base_url, endpoints }),
    });
    return textResult(result);
  }
);

server.tool(
  "fake_data",
  "Generate realistic fake/mock data for testing. Types: user, product, address, company, transaction, event.",
  {
    type: z.string().optional().default("user").describe("Data type: user, product, address, company, transaction, event"),
    count: z.number().optional().default(10).describe("Number of records (max 100)"),
  },
  async ({ type, count }) => {
    const result = await apiCall("/api/data/fake", {
      method: "POST",
      body: JSON.stringify({ type, count }),
    });
    return textResult(result);
  }
);

server.tool(
  "code_minify",
  "Minify JavaScript, CSS, or HTML code. Returns minified code with savings percentage.",
  {
    code: z.string().describe("Code to minify"),
    language: z.string().optional().default("auto").describe("Language: javascript, css, html, or auto"),
  },
  async ({ code, language }) => {
    const result = await apiCall("/api/code/minify", {
      method: "POST",
      body: JSON.stringify({ code, language }),
    });
    return textResult(result);
  }
);

server.tool(
  "code_format",
  "Auto-format/beautify code (JSON, SQL, HTML). Returns formatted code.",
  {
    code: z.string().describe("Code to format"),
    language: z.string().optional().default("auto").describe("Language: json, sql, html, or auto"),
    indent: z.number().optional().default(2).describe("Indent size"),
  },
  async ({ code, language, indent }) => {
    const result = await apiCall("/api/code/format", {
      method: "POST",
      body: JSON.stringify({ code, language, indent }),
    });
    return textResult(result);
  }
);

server.tool(
  "translate_code_pattern",
  "Get equivalent code patterns across languages (Python, JS, Go, Rust, TS).",
  {
    pattern: z.string().describe("Pattern name: http_get, read_file, json_parse, hash_sha256, env_var"),
    from: z.string().optional().default("python").describe("Source language"),
    to: z.string().optional().default("javascript").describe("Target language"),
  },
  async ({ pattern, from: fromLang, to: toLang }) => {
    const result = await apiCall("/api/text/translate-code", {
      method: "POST",
      body: JSON.stringify({ pattern, from: fromLang, to: toLang }),
    });
    return textResult(result);
  }
);

server.tool(
  "validate_json_schema",
  "Validate JSON data against a JSON Schema. Returns validation errors.",
  {
    data: z.any().describe("JSON data to validate"),
    schema: z.any().describe("JSON Schema to validate against"),
  },
  async ({ data, schema }) => {
    const result = await apiCall("/api/schema/validate", {
      method: "POST",
      body: JSON.stringify({ data, schema }),
    });
    return textResult(result);
  }
);

server.tool(
  "csv_analyze",
  "Analyze CSV data: column types, statistics, missing values, unique counts.",
  {
    csv: z.string().describe("CSV text data to analyze"),
  },
  async ({ csv }) => {
    const result = await apiCall("/api/data/csv-analyze", {
      method: "POST",
      body: JSON.stringify({ csv }),
    });
    return textResult(result);
  }
);

server.tool(
  "security_headers_check",
  "Analyze HTTP security headers of a URL. Returns score, grade, and recommendations.",
  {
    url: z.string().describe("URL to check security headers for"),
  },
  async ({ url }) => {
    const result = await apiCall("/api/security/headers-check", {
      method: "POST",
      body: JSON.stringify({ url }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_api_client",
  "Generate API client code from endpoint definitions (Python, JavaScript, cURL).",
  {
    base_url: z.string().describe("Base URL of the API"),
    endpoints: z.array(z.object({
      path: z.string(),
      method: z.string().optional().default("GET"),
      name: z.string().optional(),
    })).describe("Array of endpoint definitions"),
    language: z.string().optional().default("python").describe("Output language: python, javascript, curl"),
  },
  async ({ base_url, endpoints, language }) => {
    const result = await apiCall("/api/generate/api-client", {
      method: "POST",
      body: JSON.stringify({ base_url, endpoints, language }),
    });
    return textResult(result);
  }
);

server.tool(
  "generate_env_template",
  "Generate a .env.example template from environment variables or parse existing .env file.",
  {
    env: z.string().optional().describe("Existing .env file content to sanitize"),
    variables: z.array(z.union([z.string(), z.object({ name: z.string(), description: z.string().optional() })])).optional().describe("List of variable names or objects"),
  },
  async ({ env, variables }) => {
    const result = await apiCall("/api/generate/env-template", {
      method: "POST",
      body: JSON.stringify({ env, variables }),
    });
    return textResult(result);
  }
);

// --- New v1.15.0 Tools ---

server.tool(
  "prompt_engineer",
  "Analyze and optimize an LLM prompt. Checks for role, context, constraints, output format, and examples. Returns improved version with quality score.",
  {
    prompt: z.string().describe("The prompt to analyze and optimize"),
    model: z.string().optional().default("general").describe("Target model: general, claude, gpt"),
    style: z.string().optional().default("detailed").describe("Style: detailed, concise"),
  },
  async ({ prompt, model, style }) => {
    const result = await apiCall("/api/prompt/engineer", {
      method: "POST",
      body: JSON.stringify({ prompt, model, style }),
    });
    return textResult(result);
  }
);

server.tool(
  "changelog_generate",
  "Generate a formatted changelog from commit messages. Automatically categorizes into Added, Changed, Fixed, Removed, Security.",
  {
    commits: z.array(z.union([
      z.string(),
      z.object({ message: z.string(), type: z.string().optional() })
    ])).describe("Array of commit messages or objects with message and optional type"),
    version: z.string().optional().default("1.0.0").describe("Version number"),
    date: z.string().optional().describe("Release date (YYYY-MM-DD)"),
    format: z.string().optional().default("keepachangelog").describe("Format: keepachangelog, simple"),
  },
  async ({ commits, version, date, format }) => {
    const result = await apiCall("/api/changelog/generate", {
      method: "POST",
      body: JSON.stringify({ commits, version, date, format }),
    });
    return textResult(result);
  }
);

server.tool(
  "license_generate",
  "Generate a LICENSE file. Supports MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, ISC, Unlicense.",
  {
    type: z.string().optional().default("MIT").describe("License type: MIT, APACHE-2.0, GPL-3.0, BSD-3-CLAUSE, ISC, UNLICENSE"),
    name: z.string().optional().default("Your Name").describe("Copyright holder name"),
    year: z.number().optional().describe("Copyright year"),
  },
  async ({ type, name, year }) => {
    const result = await apiCall("/api/license/generate", {
      method: "POST",
      body: JSON.stringify({ type, name, year }),
    });
    return textResult(result);
  }
);

server.tool(
  "commit_message",
  "Generate a conventional commit message from a diff or description. Detects type (feat/fix/refactor/etc.) and scope automatically.",
  {
    diff: z.string().optional().describe("Git diff content"),
    description: z.string().optional().describe("Description of changes"),
    style: z.string().optional().default("conventional").describe("Style: conventional, gitmoji, simple"),
  },
  async ({ diff, description, style }) => {
    const result = await apiCall("/api/commit/message", {
      method: "POST",
      body: JSON.stringify({ diff, description, style }),
    });
    return textResult(result);
  }
);

server.tool(
  "api_spec_compare",
  "Compare two OpenAPI specs and detect breaking vs non-breaking changes.",
  {
    old: z.record(z.any()).describe("Old OpenAPI spec object"),
    new: z.record(z.any()).describe("New OpenAPI spec object"),
  },
  async ({ old: oldSpec, new: newSpec }) => {
    const result = await apiCall("/api/api-spec/compare", {
      method: "POST",
      body: JSON.stringify({ old: oldSpec, new: newSpec }),
    });
    return textResult(result);
  }
);

server.tool(
  "regex_generate",
  "Generate regex patterns from natural language. Supports: email, url, phone, ip, date, uuid, hex, domain, password, number, and more.",
  {
    description: z.string().describe("Natural language description (e.g., 'email address', 'phone number', 'url')"),
    test: z.string().optional().describe("Test string to match against the generated pattern"),
  },
  async ({ description, test }) => {
    const result = await apiCall("/api/regex/generate", {
      method: "POST",
      body: JSON.stringify({ description, test }),
    });
    return textResult(result);
  }
);

// --- Agent Discovery & Payment Tools ---

server.tool(
  "agent_discover",
  "Discover all available ToolPipe tools, pricing, and how to get started. Use this first to understand what tools are available.",
  {},
  async () => {
    const result = await apiCall("/api/agent/discover");
    return textResult(result);
  }
);

server.tool(
  "agent_register",
  "Register for a free API key (100 calls/day, no credit card needed). Returns your API key immediately.",
  {
    email: z.string().describe("Email address to register with"),
  },
  async ({ email }) => {
    const result = await apiCall("/api-keys/register", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    return textResult(result);
  }
);

server.tool(
  "agent_pay",
  "Initiate payment to upgrade to Pro tier (10,000 calls/day). Returns crypto payment addresses and instructions.",
  {
    email: z.string().describe("Email address associated with your API key"),
    tier: z.string().optional().default("pro").describe("Pricing tier: pro ($9.99/mo)"),
  },
  async ({ email, tier }) => {
    const result = await apiCall("/payments/agent-pay", {
      method: "POST",
      body: JSON.stringify({ email, tier }),
    });
    return textResult(result);
  }
);

server.tool(
  "verify_payment",
  "Verify a crypto payment on-chain. Submit your transaction hash after sending payment.",
  {
    order_id: z.string().describe("Order ID from agent_pay response"),
    tx_hash: z.string().describe("Transaction hash from your crypto payment"),
  },
  async ({ order_id, tx_hash }) => {
    const result = await apiCall("/payments/verify-tx", {
      method: "POST",
      body: JSON.stringify({ order_id, tx_hash }),
    });
    return textResult(result);
  }
);

server.tool(
  "pricing_info",
  "Get detailed pricing information for all tiers.",
  {},
  async () => {
    const result = await apiCall("/api/pricing");
    return textResult(result);
  }
);

// --- Start Server ---

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("ToolPipe MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
