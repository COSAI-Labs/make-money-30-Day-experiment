#!/usr/bin/env node

/**
 * ToolPipe MCP Server
 *
 * Exposes 20 essential developer utility tools via Model Context Protocol.
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

const BASE_URL =
  process.env.TOOLPIPE_BASE_URL || "https://toolpipe.dev";
const API_KEY = process.env.TOOLPIPE_API_KEY || "";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function apiCall(path, options = {}) {
  const url = new URL(path, BASE_URL);
  if (API_KEY) url.searchParams.set("api_key", API_KEY);

  const fetchOptions = {
    headers: { "Content-Type": "application/json" },
    ...options,
  };
  if (API_KEY) fetchOptions.headers["X-API-Key"] = API_KEY;

  const resp = await fetch(url.toString(), fetchOptions);
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
  }

  const ct = resp.headers.get("content-type") || "";
  if (ct.includes("application/json")) return resp.json();
  return resp.text();
}

function ok(data) {
  const text = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  return { content: [{ type: "text", text }] };
}

function err(msg) {
  return { content: [{ type: "text", text: String(msg) }], isError: true };
}

async function post(path, body) {
  return apiCall(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

async function get(path) {
  return apiCall(path);
}

// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------

const server = new McpServer(
  { name: "toolpipe", version: "1.18.0" },
  {
    capabilities: { tools: {} },
    instructions:
      "ToolPipe provides 45 developer utility APIs as MCP tools. " +
      "JSON formatting/validation/schema, QR codes, hashing, UUID, base64, " +
      "markdown-to-HTML, URL shortener, regex tester/generator, text stats, " +
      "JWT decode/create, DNS lookup, HTTP headers/proxy, SSL check, password gen, " +
      "lorem ipsum, color converter, cron parser, timestamp converter, " +
      "CSV-to-JSON, code minify/format/review/explain, fake data generation, " +
      "WHOIS lookup, Dockerfile/docker-compose generation, git commit messages, " +
      "IP geolocation, crypto prices, website screenshots, SEO analysis, " +
      "URL/HTML encode/decode, text diff, language detection, downtime checker, " +
      "and more. Free: 100 calls/day. Pro: 10,000 calls/day ($9.99/mo).",
  }
);

// ---------------------------------------------------------------------------
// 1. JSON Formatter
// ---------------------------------------------------------------------------
server.tool(
  "json_format",
  "Format, validate, and pretty-print JSON. Detects syntax errors.",
  { json: z.string().describe("JSON string to format") },
  async ({ json }) => {
    try {
      return ok(JSON.stringify(JSON.parse(json), null, 2));
    } catch (e) {
      return err(`JSON Error: ${e.message}`);
    }
  }
);

// ---------------------------------------------------------------------------
// 2. QR Code Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_qr_code",
  "Generate a QR code image URL from text or a URL.",
  {
    text: z.string().describe("Text or URL to encode"),
    size: z.number().optional().describe("Image size in pixels (default 200)"),
  },
  async ({ text, size }) => {
    try {
      const data = await post("/api/qr", { text, size: size || 200 });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 3. Hash Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_hash",
  "Generate a hash (MD5, SHA-1, SHA-256, SHA-512) of the given text.",
  {
    text: z.string().describe("Text to hash"),
    algorithm: z
      .enum(["md5", "sha1", "sha256", "sha512"])
      .optional()
      .describe("Hash algorithm (default sha256)"),
  },
  async ({ text, algorithm }) => {
    try {
      const data = await post("/api/hash", {
        text,
        algorithm: algorithm || "sha256",
      });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 4. UUID Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_uuid",
  "Generate one or more UUIDs (v4).",
  {
    count: z
      .number()
      .optional()
      .describe("Number of UUIDs to generate (default 1, max 100)"),
  },
  async ({ count }) => {
    try {
      const data = await get(`/api/uuid?count=${count || 1}`);
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 5. Base64 Encode / Decode
// ---------------------------------------------------------------------------
server.tool(
  "base64",
  "Encode or decode a Base64 string.",
  {
    text: z.string().describe("Text to encode or Base64 string to decode"),
    action: z
      .enum(["encode", "decode"])
      .optional()
      .describe("encode or decode (default encode)"),
  },
  async ({ text, action }) => {
    try {
      const data = await post("/api/base64", {
        text,
        action: action || "encode",
      });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 6. Markdown to HTML
// ---------------------------------------------------------------------------
server.tool(
  "markdown_to_html",
  "Convert Markdown text to HTML.",
  { markdown: z.string().describe("Markdown text to convert") },
  async ({ markdown }) => {
    try {
      const data = await post("/api/markdown", { markdown });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 7. URL Shortener
// ---------------------------------------------------------------------------
server.tool(
  "shorten_url",
  "Shorten a long URL.",
  { url: z.string().describe("URL to shorten") },
  async ({ url }) => {
    try {
      const data = await post("/api/shorten", { url });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 8. Regex Tester
// ---------------------------------------------------------------------------
server.tool(
  "regex_test",
  "Test a regular expression against a string. Returns matches.",
  {
    pattern: z.string().describe("Regular expression pattern"),
    text: z.string().describe("Text to test against"),
    flags: z.string().optional().describe("Regex flags (default 'g')"),
  },
  async ({ pattern, text, flags }) => {
    try {
      const data = await post("/api/regex", {
        pattern,
        text,
        flags: flags || "g",
      });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 9. Text Stats
// ---------------------------------------------------------------------------
server.tool(
  "text_stats",
  "Analyze text: word count, character count, sentence count, reading time.",
  { text: z.string().describe("Text to analyze") },
  async ({ text }) => {
    try {
      const data = await post("/api/text-stats", { text });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 10. JWT Decode
// ---------------------------------------------------------------------------
server.tool(
  "jwt_decode",
  "Decode a JSON Web Token (JWT) and return its header and payload.",
  { token: z.string().describe("JWT token string") },
  async ({ token }) => {
    try {
      const data = await post("/api/jwt/decode", { token });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 11. DNS Lookup
// ---------------------------------------------------------------------------
server.tool(
  "dns_lookup",
  "Perform a DNS lookup for a domain. Returns A, AAAA, MX, TXT, NS records.",
  {
    domain: z.string().describe("Domain name to look up"),
    type: z
      .enum(["A", "AAAA", "MX", "TXT", "NS", "CNAME", "SOA"])
      .optional()
      .describe("Record type (default A)"),
  },
  async ({ domain, type }) => {
    try {
      const data = await get(
        `/api/dns?domain=${encodeURIComponent(domain)}&type=${type || "A"}`
      );
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 12. HTTP Headers Check
// ---------------------------------------------------------------------------
server.tool(
  "http_headers",
  "Fetch and display HTTP response headers for a URL.",
  { url: z.string().describe("URL to check headers for") },
  async ({ url }) => {
    try {
      const data = await get(
        `/api/http-headers?url=${encodeURIComponent(url)}`
      );
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 13. SSL Certificate Check
// ---------------------------------------------------------------------------
server.tool(
  "ssl_check",
  "Check SSL/TLS certificate details for a domain.",
  { domain: z.string().describe("Domain to check SSL certificate") },
  async ({ domain }) => {
    try {
      const data = await get(
        `/api/ssl?domain=${encodeURIComponent(domain)}`
      );
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 14. Password Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_password",
  "Generate a strong random password.",
  {
    length: z
      .number()
      .optional()
      .describe("Password length (default 16, max 128)"),
    uppercase: z
      .boolean()
      .optional()
      .describe("Include uppercase letters (default true)"),
    numbers: z
      .boolean()
      .optional()
      .describe("Include numbers (default true)"),
    symbols: z
      .boolean()
      .optional()
      .describe("Include symbols (default true)"),
  },
  async ({ length, uppercase, numbers, symbols }) => {
    try {
      const data = await post("/api/password", {
        length: length || 16,
        uppercase: uppercase !== false,
        numbers: numbers !== false,
        symbols: symbols !== false,
      });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 15. Lorem Ipsum Generator
// ---------------------------------------------------------------------------
server.tool(
  "lorem_ipsum",
  "Generate lorem ipsum placeholder text.",
  {
    paragraphs: z
      .number()
      .optional()
      .describe("Number of paragraphs (default 1)"),
    type: z
      .enum(["paragraphs", "sentences", "words"])
      .optional()
      .describe("Output type (default paragraphs)"),
  },
  async ({ paragraphs, type }) => {
    try {
      const data = await get(
        `/api/lorem?count=${paragraphs || 1}&type=${type || "paragraphs"}`
      );
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 16. Color Converter
// ---------------------------------------------------------------------------
server.tool(
  "convert_color",
  "Convert a color between HEX, RGB, and HSL formats.",
  {
    color: z
      .string()
      .describe("Color value (e.g. '#ff5733', 'rgb(255,87,51)', 'hsl(11,100%,60%)')"),
  },
  async ({ color }) => {
    try {
      const data = await get(
        `/api/color?color=${encodeURIComponent(color)}`
      );
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 17. Cron Expression Parser
// ---------------------------------------------------------------------------
server.tool(
  "parse_cron",
  "Parse a cron expression and return its human-readable schedule.",
  {
    expression: z
      .string()
      .describe("Cron expression (e.g. '*/5 * * * *')"),
  },
  async ({ expression }) => {
    try {
      const data = await post("/api/cron", { expression });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 18. Timestamp Converter
// ---------------------------------------------------------------------------
server.tool(
  "convert_timestamp",
  "Convert between Unix timestamps and ISO 8601 date strings.",
  {
    value: z
      .string()
      .describe(
        "Unix timestamp (seconds or ms) or ISO 8601 date string"
      ),
  },
  async ({ value }) => {
    try {
      const data = await post("/api/timestamp", { value });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 19. CSV to JSON
// ---------------------------------------------------------------------------
server.tool(
  "csv_to_json",
  "Convert CSV text to JSON array.",
  {
    csv: z.string().describe("CSV data to convert"),
    delimiter: z
      .string()
      .optional()
      .describe("Column delimiter (default ',')"),
  },
  async ({ csv, delimiter }) => {
    try {
      const data = await post("/api/csv-to-json", {
        csv,
        delimiter: delimiter || ",",
      });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 20. Code Minifier
// ---------------------------------------------------------------------------
server.tool(
  "minify_code",
  "Minify JavaScript, CSS, or HTML code by removing whitespace and comments.",
  {
    code: z.string().describe("Code to minify"),
    language: z
      .enum(["javascript", "css", "html"])
      .optional()
      .describe("Language (default javascript)"),
  },
  async ({ code, language }) => {
    try {
      const data = await post("/api/minify", {
        code,
        language: language || "javascript",
      });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 21. Code Review
// ---------------------------------------------------------------------------
server.tool(
  "code_review",
  "Review code for bugs, security issues, and best practices. Returns detailed feedback.",
  {
    code: z.string().describe("Code to review"),
    language: z.string().optional().describe("Programming language (auto-detected if omitted)"),
  },
  async ({ code, language }) => {
    try {
      const data = await post("/api/code/review", { code, language });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 22. Code Explain
// ---------------------------------------------------------------------------
server.tool(
  "code_explain",
  "Explain what a piece of code does in plain English.",
  {
    code: z.string().describe("Code to explain"),
    language: z.string().optional().describe("Programming language"),
  },
  async ({ code, language }) => {
    try {
      const data = await post("/api/code/explain", { code, language });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 23. Code Format
// ---------------------------------------------------------------------------
server.tool(
  "code_format",
  "Format/beautify code (JavaScript, Python, SQL, JSON, HTML, CSS, and more).",
  {
    code: z.string().describe("Code to format"),
    language: z.string().optional().describe("Programming language (default javascript)"),
  },
  async ({ code, language }) => {
    try {
      const data = await post("/api/code/format", { code, language: language || "javascript" });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 24. Fake Data Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_fake_data",
  "Generate realistic fake/mock data (names, emails, addresses, companies, etc.).",
  {
    type: z.string().describe("Data type: person, company, address, email, phone, creditcard, product, user"),
    count: z.number().optional().describe("Number of records (default 1, max 100)"),
    locale: z.string().optional().describe("Locale (default en)"),
  },
  async ({ type, count, locale }) => {
    try {
      const data = await post("/api/data/fake", { type, count: count || 1, locale: locale || "en" });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 25. JSON Schema Validate
// ---------------------------------------------------------------------------
server.tool(
  "json_schema_validate",
  "Validate JSON data against a JSON Schema.",
  {
    data: z.string().describe("JSON data to validate"),
    schema: z.string().describe("JSON Schema to validate against"),
  },
  async ({ data, schema }) => {
    try {
      const parsed_data = JSON.parse(data);
      const parsed_schema = JSON.parse(schema);
      const result = await post("/api/schema/validate", { data: parsed_data, schema: parsed_schema });
      return ok(result);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 26. WHOIS Lookup
// ---------------------------------------------------------------------------
server.tool(
  "whois_lookup",
  "Look up WHOIS registration info for a domain.",
  {
    domain: z.string().describe("Domain name to look up"),
  },
  async ({ domain }) => {
    try {
      const data = await get(`/api/whois?domain=${encodeURIComponent(domain)}`);
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 27. Dockerfile Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_dockerfile",
  "Generate a Dockerfile for a project based on language and framework.",
  {
    language: z.string().describe("Programming language (node, python, go, rust, java, etc.)"),
    framework: z.string().optional().describe("Framework (express, fastapi, gin, etc.)"),
    port: z.number().optional().describe("Port to expose"),
  },
  async ({ language, framework, port }) => {
    try {
      const data = await post("/api/dockerfile/generate", { language, framework, port });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 28. Docker Compose Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_docker_compose",
  "Generate a docker-compose.yml for a multi-service stack.",
  {
    services: z.string().describe("Comma-separated services (e.g. 'node,postgres,redis')"),
  },
  async ({ services }) => {
    try {
      const data = await post("/api/generate/docker-compose", { services });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 29. Git Commit Message Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_commit_message",
  "Generate a conventional git commit message from a code diff or description.",
  {
    diff: z.string().optional().describe("Git diff or code changes"),
    description: z.string().optional().describe("Description of what changed"),
    style: z.string().optional().describe("Style: conventional, angular, simple (default conventional)"),
  },
  async ({ diff, description, style }) => {
    try {
      const data = await post("/api/commit/message", { diff, description, style: style || "conventional" });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 30. Regex Generator
// ---------------------------------------------------------------------------
server.tool(
  "generate_regex",
  "Generate a regex pattern from a natural language description.",
  {
    description: z.string().describe("What the regex should match (e.g. 'email addresses', 'US phone numbers')"),
    test_strings: z.array(z.string()).optional().describe("Strings to test the regex against"),
  },
  async ({ description, test_strings }) => {
    try {
      const data = await post("/api/regex/generate", { description, test_strings });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 31. SQL Formatter
// ---------------------------------------------------------------------------
server.tool(
  "sql_format",
  "Format and beautify SQL queries.",
  {
    sql: z.string().describe("SQL query to format"),
    dialect: z.string().optional().describe("SQL dialect: standard, postgresql, mysql, sqlite"),
  },
  async ({ sql, dialect }) => {
    try {
      const data = await post("/api/sql/format", { sql, dialect });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 32. JSON to TypeScript Interface
// ---------------------------------------------------------------------------
server.tool(
  "json_to_typescript",
  "Generate TypeScript interfaces from JSON data.",
  {
    json: z.string().describe("JSON data to generate interfaces from"),
    name: z.string().optional().describe("Root interface name (default Root)"),
  },
  async ({ json, name }) => {
    try {
      const data = await post("/api/generate/typescript-interface", { json, name });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 33. JWT Create
// ---------------------------------------------------------------------------
server.tool(
  "jwt_create",
  "Create a JWT token with custom payload and secret.",
  {
    payload: z.string().describe("JSON payload for the token"),
    secret: z.string().describe("Secret key for signing"),
    expires_in: z.string().optional().describe("Expiration (e.g. '1h', '7d', '30m')"),
  },
  async ({ payload, secret, expires_in }) => {
    try {
      const parsed = JSON.parse(payload);
      const data = await post("/api/jwt/create", { payload: parsed, secret, expires_in });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 34. Web Extract (Scrape)
// ---------------------------------------------------------------------------
server.tool(
  "web_extract",
  "Extract structured content from a URL (title, text, links, meta tags).",
  {
    url: z.string().describe("URL to extract content from"),
    selectors: z.array(z.string()).optional().describe("CSS selectors to extract specific elements"),
  },
  async ({ url, selectors }) => {
    try {
      const data = await post("/api/web/extract", { url, selectors });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 35. Prompt Engineer
// ---------------------------------------------------------------------------
server.tool(
  "prompt_engineer",
  "Improve and optimize an LLM prompt. Returns an enhanced version with best practices.",
  {
    prompt: z.string().describe("The prompt to improve"),
    model: z.string().optional().describe("Target model (gpt-4, claude, llama, etc.)"),
    task: z.string().optional().describe("Task type: chat, code, analysis, creative"),
  },
  async ({ prompt, model, task }) => {
    try {
      const data = await post("/api/prompt/engineer", { prompt, model, task });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 36. IP Lookup
// ---------------------------------------------------------------------------
server.tool(
  "ip_lookup",
  "Get geolocation and ISP info for an IP address.",
  {
    ip: z.string().optional().describe("IP address (omit for your own IP)"),
  },
  async ({ ip }) => {
    try {
      const data = await get(ip ? `/api/ip?ip=${encodeURIComponent(ip)}` : "/api/ip/my");
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 37. Crypto Prices
// ---------------------------------------------------------------------------
server.tool(
  "crypto_prices",
  "Get current cryptocurrency prices (BTC, ETH, SOL, etc.).",
  {
    coins: z.string().optional().describe("Comma-separated coin symbols (default: btc,eth,sol)"),
  },
  async ({ coins }) => {
    try {
      const data = await get(`/api/crypto/prices${coins ? `?coins=${encodeURIComponent(coins)}` : ""}`);
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 38. Website Screenshot
// ---------------------------------------------------------------------------
server.tool(
  "screenshot",
  "Take a screenshot of a website and return the image URL.",
  {
    url: z.string().describe("URL to screenshot"),
    width: z.number().optional().describe("Viewport width (default 1280)"),
    height: z.number().optional().describe("Viewport height (default 800)"),
  },
  async ({ url, width, height }) => {
    try {
      const data = await post("/api/screenshot", { url, width: width || 1280, height: height || 800 });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 39. HTTP Request Proxy
// ---------------------------------------------------------------------------
server.tool(
  "http_request",
  "Make an HTTP request to any URL and return the response. Useful for agents that cannot make direct HTTP calls.",
  {
    url: z.string().describe("URL to request"),
    method: z.enum(["GET", "POST", "PUT", "DELETE", "PATCH"]).optional().describe("HTTP method (default GET)"),
    headers: z.string().optional().describe("JSON object of request headers"),
    body: z.string().optional().describe("Request body (for POST/PUT/PATCH)"),
  },
  async ({ url, method, headers, body }) => {
    try {
      const payload = { url, method: method || "GET" };
      if (headers) payload.headers = JSON.parse(headers);
      if (body) payload.body = body;
      const data = await post("/api/http/request", payload);
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 40. SEO Analyzer
// ---------------------------------------------------------------------------
server.tool(
  "seo_analyze",
  "Analyze a URL for SEO: meta tags, headings, performance hints, accessibility.",
  {
    url: z.string().describe("URL to analyze for SEO"),
  },
  async ({ url }) => {
    try {
      const data = await get(`/api/seo?url=${encodeURIComponent(url)}`);
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 41. URL Encode/Decode
// ---------------------------------------------------------------------------
server.tool(
  "url_encode_decode",
  "URL-encode or decode a string.",
  {
    text: z.string().describe("Text to encode or decode"),
    action: z.enum(["encode", "decode"]).optional().describe("encode or decode (default encode)"),
  },
  async ({ text, action }) => {
    try {
      const data = await post("/api/url/encode-decode", { text, action: action || "encode" });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 42. HTML Encode/Decode
// ---------------------------------------------------------------------------
server.tool(
  "html_encode_decode",
  "HTML-encode or decode a string (escape special characters).",
  {
    text: z.string().describe("Text to encode or decode"),
    action: z.enum(["encode", "decode"]).optional().describe("encode or decode (default encode)"),
  },
  async ({ text, action }) => {
    try {
      const data = await post("/api/html/encode-decode", { text, action: action || "encode" });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 43. Text Diff
// ---------------------------------------------------------------------------
server.tool(
  "text_diff",
  "Compare two texts and show differences (unified diff format).",
  {
    text1: z.string().describe("Original text"),
    text2: z.string().describe("Modified text"),
  },
  async ({ text1, text2 }) => {
    try {
      const data = await post("/api/text/diff", { text1, text2 });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 44. Language Detector
// ---------------------------------------------------------------------------
server.tool(
  "detect_language",
  "Detect the natural language of a text.",
  {
    text: z.string().describe("Text to detect language of"),
  },
  async ({ text }) => {
    try {
      const data = await post("/api/text/detect-language", { text });
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// 45. Website Down Checker
// ---------------------------------------------------------------------------
server.tool(
  "is_website_down",
  "Check if a website is up or down.",
  {
    url: z.string().describe("URL or domain to check"),
  },
  async ({ url }) => {
    try {
      const data = await get(`/api/down?url=${encodeURIComponent(url)}`);
      return ok(data);
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((e) => {
  console.error("Fatal:", e);
  process.exit(1);
});
