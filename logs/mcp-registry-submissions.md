# MCP Registry & Directory Submissions

## Date: 2026-04-02

### COMPLETED SUBMISSIONS

1. **modelcontextprotocol/servers (Official MCP Servers repo)**
   - Method: GitHub Issue
   - URL: https://github.com/modelcontextprotocol/servers/issues/3785
   - Status: SUBMITTED (pending review)

2. **mcp.so (chatmcp/mcpso)**
   - Method: GitHub Issue comment on chatmcp/mcpso#1
   - URL: https://github.com/chatmcp/mcpso/issues/1#issuecomment-4173685440
   - Status: SUBMITTED (pending listing)

3. **Cline MCP Marketplace**
   - Method: GitHub Issue
   - URL: https://github.com/cline/mcp-marketplace/issues/1201
   - Status: SUBMITTED (pending review)

4. **MCP Repository (mcprepository.com)**
   - Method: CLI tool (npx mcp-index)
   - Expected URL: https://mcprepository.com/cosai-labs/make-money-30day-challenge
   - Status: SUBMITTED (queued for validation)

### REQUIRES MANUAL/BROWSER ACTION

5. **PulseMCP (pulsemcp.com/submit)**
   - Method: Web form (Cloudflare-protected, no API)
   - Form fields: Type = "MCP Server", URL = GitHub repo URL
   - Status: NEEDS BROWSER (form blocked by Cloudflare for curl)
   - Alt path: Will auto-ingest once listed in official MCP Registry

6. **Official MCP Registry (registry.modelcontextprotocol.io)**
   - Method: mcp-publisher CLI (installed at ~/.npm-global/bin/mcp-publisher)
   - server.json created and validated at: products/mcp-server-package/server.json
   - Status: NEEDS INTERACTIVE AUTH (GitHub device flow requires browser)
   - To complete:
     1. Run: `cd products/mcp-server-package && mcp-publisher login github`
     2. Open the URL shown, enter the device code
     3. Run: `mcp-publisher publish`

7. **MCPize (mcpize.com) - 85% Revenue Share**
   - Method: MCPize CLI (npx mcpize login, then mcpize deploy)
   - Status: NEEDS BROWSER AUTH (OAuth login via browser)
   - To complete:
     1. Run: `cd products/mcp-server-package && npx mcpize login`
     2. Open the URL shown, complete auth
     3. Run: `npx mcpize deploy`

8. **mcp.directory**
   - Method: Web form at https://mcp.directory/submit
   - Fields: GitHub URL (required), npm package, description, email
   - Status: NEEDS BROWSER (client-side React form)

9. **mcpservers.org (Awesome MCP Servers)**
   - Method: Web form at https://mcpservers.org/submit
   - Fields: name, description, URL, category (development), email
   - Status: NEEDS BROWSER (TanStack client-side form)

10. **Glama (glama.ai/mcp/servers)**
    - Method: Web form (Add Server button)
    - Status: NEEDS BROWSER

### NOT YET ATTEMPTED (Require Accounts/Payment)

11. **AIAgentsList (aiagentslist.com/submit)**
    - Requires account/dashboard login
    - Status: NEEDS ACCOUNT CREATION

12. **DevHunt (devhunt.org)**
    - Requires login to submit
    - Status: NEEDS ACCOUNT CREATION

13. **There's An AI For That (theresanaiforthat.com/submit)**
    - Requires $347 one-off payment (or free via monthly X/Twitter thread)
    - Status: SKIPPED (paid, not worth it currently)

14. **SaaSHub (saashub.com/submit/list)**
    - Free submission, requires account
    - Status: NEEDS ACCOUNT CREATION

### PREVIOUSLY SUBMITTED (20 PRs to awesome-mcp-servers lists)
- See existing PRs on GitHub for awesome-mcp-servers lists

### server.json for Official Registry
Location: products/mcp-server-package/server.json
Validated successfully against registry.modelcontextprotocol.io
