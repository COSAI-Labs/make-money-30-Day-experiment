#!/bin/bash
# Publish ToolPipe MCP Server v1.21.0 to Official MCP Registry
# Requires GitHub API rate limit to be available

cd /home/GerritRoskaBot/make-money-30day-challenge

# Step 1: Get JWT token from registry via GitHub PAT
echo "Getting JWT from registry..."
JWT_RESPONSE=$(curl -s -X POST "https://registry.modelcontextprotocol.io/v0.1/auth/github-at" \
  -H "Content-Type: application/json" \
  -d '{"github_token": "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"}')

echo "Auth response: $JWT_RESPONSE"

# Extract JWT token
JWT=$(echo "$JWT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('registry_token',''))" 2>/dev/null)

if [ -z "$JWT" ]; then
  echo "ERROR: Failed to get JWT token"
  echo "Response: $JWT_RESPONSE"
  exit 1
fi

echo "Got JWT token: ${JWT:0:20}..."

# Step 2: Publish server.json
echo "Publishing v1.21.0..."
PUBLISH_RESPONSE=$(curl -s -X POST "https://registry.modelcontextprotocol.io/v0/publish" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -d @products/mcp-server/server.json)

echo "Publish response: $PUBLISH_RESPONSE"

# Verify
echo "Verifying..."
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=toolpipe-mcp-server&limit=1" | python3 -m json.tool 2>/dev/null | head -20

echo "Done at $(date)"
