#!/usr/bin/env node

/**
 * ToolPipe MCP Server
 *
 * Exposes 89 developer utility tools via Model Context Protocol.
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
  { name: "toolpipe", version: "1.9.1" },
  {
    capabilities: { tools: {} },
    instructions: "ToolPipe provides 130+ developer utility APIs as 88 MCP tools. JSON formatting, QR codes, hashing, UUID, DNS, base64, SQL formatting, XML/YAML conversion, text stats/readability, HTML stripping, number formatting, .env parsing, HTTP status codes, JWT create/decode, IP info, regex testing, password checking, color palettes, text diffing, and more. Free: 100 calls/day (no signup). Pro: 10,000 calls/day ($9.99).",
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
