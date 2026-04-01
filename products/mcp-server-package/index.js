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
  { name: "toolpipe", version: "1.0.0" },
  {
    capabilities: { tools: {} },
    instructions:
      "ToolPipe provides 20 essential developer utility APIs as MCP tools. " +
      "JSON formatting, QR codes, hashing, UUID, base64, markdown-to-HTML, " +
      "URL shortener, regex tester, text stats, JWT decode, DNS lookup, " +
      "HTTP headers check, SSL check, password generator, lorem ipsum, " +
      "color converter, cron parser, timestamp converter, CSV-to-JSON, and " +
      "code minification. Free: 100 calls/day. Pro: 10,000 calls/day ($9.99/mo).",
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
