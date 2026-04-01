#!/usr/bin/env node

/**
 * ToolPipe MCP Server
 *
 * Exposes 20+ developer utility tools via Model Context Protocol.
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

const BASE_URL = process.env.TOOLPIPE_BASE_URL || "https://toolpipe.dev";
const API_KEY = process.env.TOOLPIPE_API_KEY || "";

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
  { name: "toolpipe", version: "1.0.0" },
  {
    capabilities: { tools: {} },
    instructions: "ToolPipe provides 70+ developer utility APIs. Use these tools for JSON formatting, QR code generation, hashing, UUID generation, DNS lookup, base64 encoding, markdown conversion, text analysis, and more. Get a free API key at /api-keys for 100 calls/day, or upgrade to Pro for 10,000 calls/day.",
  }
);

// --- Tool Definitions ---

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
    const result = await apiCall(`/uuid/generate?count=${count || 1}`);
    return textResult(result);
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
    const result = await apiCall("/hash/generate", {
      method: "POST",
      body: JSON.stringify({ text, algorithm: algorithm || "sha256" }),
    });
    return textResult(result);
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
    const result = await apiCall("/base64", {
      method: "POST",
      body: JSON.stringify({ text, action: action || "encode" }),
    });
    return textResult(result);
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
