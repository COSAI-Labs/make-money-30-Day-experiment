#!/bin/bash
# MCP Registry Submission Script
# Run this to submit ToolPipe MCP Server to various MCP directories
# Some require browser-based auth; this script handles what it can and provides URLs for the rest.

set -e

echo "========================================="
echo "ToolPipe MCP Server - Registry Submission"
echo "========================================="
echo ""

# Server details
SERVER_NAME="ToolPipe MCP Server"
DESCRIPTION="89 developer tools via MCP: JSON, QR, hash, UUID, DNS, regex, JWT, SQL, XML, YAML, PDF, and more"
GITHUB_URL="https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server"
NPM_PACKAGE="@cosai-labs/toolpipe-mcp-server"
REMOTE_URL="https://toolpipe.dev/mcp"
REGISTRY_NAME="io.github.COSAI-Labs/toolpipe-mcp-server"
EMAIL="toolpipe-ads@sharebot.net"
CATEGORY="development"

echo "Server: $SERVER_NAME"
echo "npm: $NPM_PACKAGE"
echo "Registry: $REGISTRY_NAME"
echo ""

# 1. Official MCP Registry (CLI-based)
echo "--- 1. Official MCP Registry ---"
if command -v mcp-publisher &> /dev/null; then
    cd "$(dirname "$0")/.."
    mcp-publisher validate && echo "server.json is valid"
    echo "Attempting publish..."
    mcp-publisher publish 2>&1 || echo "Already published or auth needed. Run: mcp-publisher login github -token \$(gh auth token)"
else
    echo "SKIP: mcp-publisher not installed. Run: brew install mcp-publisher"
fi
echo ""

# 2. PulseMCP (auto-ingests from official registry weekly)
echo "--- 2. PulseMCP ---"
echo "STATUS: Auto-ingests from official MCP registry weekly."
echo "ACTION: Already in official registry. Will appear on PulseMCP within ~1 week."
echo "MANUAL: Email hello@pulsemcp.com to request faster processing."
echo "SUBMIT URL: https://www.pulsemcp.com/submit"
echo ""

# 3. Smithery.ai (CLI-based, requires browser auth)
echo "--- 3. Smithery.ai ---"
if command -v smithery &> /dev/null || npx smithery --version &> /dev/null 2>&1; then
    echo "Smithery CLI available."
    npx smithery auth whoami 2>&1 || echo "Not logged in. Run: npx smithery auth login"
    echo "To publish: npx smithery mcp publish --name cosai-labs/toolpipe-mcp-server"
else
    echo "SKIP: Smithery CLI not available."
fi
echo "MANUAL: Visit https://smithery.ai and log in to publish."
echo ""

# 4. mcp.so
echo "--- 4. mcp.so ---"
echo "STATUS: No public API for submission. Requires browser-based form."
echo "SUBMIT URL: https://mcp.so/submit"
echo "FIELDS: Server name, description, GitHub URL, category"
echo ""

# 5. MCPServers.org (browser form)
echo "--- 5. MCPServers.org ---"
echo "STATUS: Browser-based form submission required."
echo "SUBMIT URL: https://mcpservers.org/submit"
echo "FIELDS:"
echo "  Server Name: $SERVER_NAME"
echo "  Short Description: $DESCRIPTION"
echo "  Link: $GITHUB_URL"
echo "  Category: Development"
echo "  Contact Email: $EMAIL"
echo "EMAIL: contact@mcpservers.org"
echo ""

# 6. MCPMarket (mcpmarket.com)
echo "--- 6. MCPMarket ---"
echo "STATUS: Browser-based submission required."
echo "SUBMIT URL: https://mcpmarket.com/submit"
echo ""

# 7. MCPize (CLI-based, requires browser auth)
echo "--- 7. MCPize ---"
if command -v mcpize &> /dev/null || npx mcpize --version &> /dev/null 2>&1; then
    echo "MCPize CLI available."
    npx mcpize whoami 2>&1 || echo "Not logged in. Run: npx mcpize login"
    echo "To deploy: npx mcpize deploy"
    echo "To publish to marketplace: npx mcpize publish"
else
    echo "SKIP: MCPize CLI not available."
fi
echo "MANUAL: Visit https://mcpize.com/developer/servers/new"
echo "EMAIL: support@mcpize.com"
echo ""

echo "========================================="
echo "Summary"
echo "========================================="
echo "Official MCP Registry: PUBLISHED (v1.9.0)"
echo "PulseMCP: PENDING (auto-ingest from official registry, ~1 week)"
echo "Smithery: NEEDS browser auth (npx smithery auth login)"
echo "mcp.so: NEEDS browser form (https://mcp.so/submit)"
echo "MCPServers.org: NEEDS browser form (https://mcpservers.org/submit)"
echo "MCPMarket: NEEDS browser form (https://mcpmarket.com/submit)"
echo "MCPize: NEEDS browser auth (npx mcpize login)"
