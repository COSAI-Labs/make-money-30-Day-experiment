#!/bin/bash
# Publish ToolPipe articles to dev.to
# Usage: DEVTO_API_KEY=your_key ./publish-to-devto.sh
# Or: source .env && ./publish-to-devto.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="/home/GerritRoskaBot/make-money-30day-challenge/.env"

# Load API key from .env if not set
if [ -z "$DEVTO_API_KEY" ] && [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

if [ -z "$DEVTO_API_KEY" ]; then
    echo "ERROR: DEVTO_API_KEY not set. Set it in .env or pass as environment variable."
    exit 1
fi

echo "Publishing Article 1..."
RESULT1=$(curl -s -w "\n%{http_code}" -X POST https://dev.to/api/articles \
  -H "Content-Type: application/json" \
  -H "api-key: $DEVTO_API_KEY" \
  -d @"$SCRIPT_DIR/devto-article-01-payload.json")

HTTP1=$(echo "$RESULT1" | tail -1)
BODY1=$(echo "$RESULT1" | head -n -1)

if [ "$HTTP1" = "201" ]; then
    URL1=$(echo "$BODY1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))" 2>/dev/null)
    echo "  SUCCESS: $URL1"
else
    echo "  FAILED (HTTP $HTTP1): $BODY1"
fi

echo ""
echo "Publishing Article 2..."
RESULT2=$(curl -s -w "\n%{http_code}" -X POST https://dev.to/api/articles \
  -H "Content-Type: application/json" \
  -H "api-key: $DEVTO_API_KEY" \
  -d @"$SCRIPT_DIR/devto-article-02-payload.json")

HTTP2=$(echo "$RESULT2" | tail -1)
BODY2=$(echo "$RESULT2" | head -n -1)

if [ "$HTTP2" = "201" ]; then
    URL2=$(echo "$BODY2" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))" 2>/dev/null)
    echo "  SUCCESS: $URL2"
else
    echo "  FAILED (HTTP $HTTP2): $BODY2"
fi

echo ""
echo "Done."
