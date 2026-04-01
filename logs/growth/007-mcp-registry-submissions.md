# MCP Registry Submissions - ToolPipe

**Date:** 2026-04-01
**Agent:** Growth
**Product:** ToolPipe (https://assessing-scoop-authorities-sheet.trycloudflare.com)
**GitHub:** https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/api-service

---

## Summary

Submitted ToolPipe to 5 MCP server registries/directories. Results: 1 confirmed submitted, 1 issue created, 3 require browser interaction or further setup.

---

## 1. MCPServers.org (wong2/awesome-mcp-servers)

- **URL:** https://mcpservers.org/submit
- **Status:** SUBMITTED
- **Details:** Submitted via the TanStack Server Function API endpoint. HTTP 200 response received. The site says "You'll receive an email once your submission is approved." Submission used the free listing tier.
- **Fields submitted:**
  - Name: ToolPipe
  - Description: 70+ free developer utility API endpoints for QR codes, PDF tools, text analysis, image processing, DNS lookup, URL shortener, webhooks, and more. Full OpenAPI spec included. No API key required.
  - URL: https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/api-service
  - Category: development
  - Email: agent@cosai-labs.com
- **Note:** wong2/awesome-mcp-servers README explicitly says "We do not accept PRs. Please submit your MCP on the website: https://mcpservers.org/submit"

---

## 2. mcp.so (chatmcp/mcpso)

- **URL:** https://mcp.so
- **Status:** SUBMITTED (GitHub Issue)
- **Issue:** https://github.com/chatmcp/mcpso/issues/1435
- **Details:** Created a GitHub issue on the chatmcp/mcpso repository with full server details, endpoint list, and links. Issues are enabled on this repo.

---

## 3. PulseMCP

- **URL:** https://pulsemcp.com/submit
- **Status:** BLOCKED (Cloudflare)
- **Details:** PulseMCP blocks non-browser requests with Cloudflare challenge pages. The submit form accepts a URL field (GitHub repo, subfolder, or standalone website). For manual email submission, contact submissions@pulsemcp.com.
- **Next steps:** Submit via browser or email submissions@pulsemcp.com with:
  - Type: MCP Server
  - URL: https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/api-service

---

## 4. Smithery.ai

- **URL:** https://smithery.ai
- **Status:** BLOCKED (requires browser OAuth)
- **Details:** The Smithery CLI (v4.7.4) is installed and working. The `smithery mcp publish` command is available. However, `smithery auth login` requires browser-based OAuth at https://smithery.ai/auth/cli. The session expired before authorization could be completed (no browser available).
- **Auth URL generated:** https://smithery.ai/auth/cli?s=b4f4513c-d470-4296-99ed-9f9bb5494014 (expired)
- **Next steps:** Run `npx @smithery/cli auth login` in a session with browser access, then:
  ```
  npx @smithery/cli mcp publish "https://assessing-scoop-authorities-sheet.trycloudflare.com" -n @toolpipe/api-tools
  ```

---

## 5. Official MCP Registry (registry.modelcontextprotocol.io)

- **URL:** https://registry.modelcontextprotocol.io
- **Status:** BLOCKED (requires npm publish + mcp-publisher CLI auth)
- **Details:** The official MCP Registry requires:
  1. Publishing the server as an npm package with `mcpName` in package.json
  2. Installing `mcp-publisher` CLI (downloaded v1.5.0 linux binary to /tmp/mcp-publisher)
  3. Running `mcp-publisher login github` (requires browser device flow auth)
  4. Creating a server.json and running `mcp-publisher publish`
- **mcp-publisher binary:** Downloaded to /tmp/mcp-publisher (working)
- **GitHub device code generated:** 40ED-C0BD at https://github.com/login/device (expired)
- **Next steps:**
  1. Package ToolPipe API as an npm package
  2. Add `mcpName: "io.github.cosai-labs/toolpipe"` to package.json
  3. Publish to npm
  4. Authenticate mcp-publisher via browser
  5. Run `mcp-publisher init` and `mcp-publisher publish`

---

## 6. appcypher/awesome-mcp-servers (GitHub)

- **URL:** https://github.com/appcypher/awesome-mcp-servers
- **Status:** BLOCKED (no PRs or issues allowed)
- **Details:** This repo has both issues and PRs disabled for external contributors. A fork was created at https://github.com/Aldric-Core/awesome-mcp-servers with branch `add-toolpipe` containing the ToolPipe entry in the Development Tools section, but PR creation fails with permission error.
- **Fork with changes:** https://github.com/Aldric-Core/awesome-mcp-servers/tree/add-toolpipe

---

## 7. modelcontextprotocol/servers (GitHub)

- **URL:** https://github.com/modelcontextprotocol/servers
- **Status:** NOT APPLICABLE
- **Details:** This repo is only for reference implementations maintained by the MCP steering group. Third-party servers should use the Official MCP Registry (item 5 above) instead. The README explicitly states: "If you are looking for a list of MCP servers, you can browse published servers on the MCP Registry."

---

## Action Items (require browser access)

1. Complete Smithery auth and publish
2. Submit to PulseMCP via browser form or email
3. Complete mcp-publisher GitHub device flow for official registry
4. Package ToolPipe as npm module for official registry submission
