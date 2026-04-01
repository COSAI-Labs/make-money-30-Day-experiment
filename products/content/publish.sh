#!/bin/bash
# Publish articles to dev.to via their API
# Usage: ./publish.sh <article_file.md> [DEVTO_API_KEY]

set -e

ARTICLE_FILE="${1:?Usage: ./publish.sh <article.md> [DEVTO_API_KEY]}"
DEVTO_KEY="${2:-$DEVTO_API_KEY}"

if [ -z "$DEVTO_KEY" ]; then
    echo "Error: No dev.to API key. Set DEVTO_API_KEY env var or pass as second arg."
    exit 1
fi

if [ ! -f "$ARTICLE_FILE" ]; then
    echo "Error: File not found: $ARTICLE_FILE"
    exit 1
fi

# Extract frontmatter
TITLE=$(grep '^title:' "$ARTICLE_FILE" | head -1 | sed 's/^title: *"*//;s/"*$//')
TAGS=$(grep '^tags:' "$ARTICLE_FILE" | head -1 | sed 's/^tags: *//')
CANONICAL=$(grep '^canonical_url:' "$ARTICLE_FILE" | head -1 | sed 's/^canonical_url: *//')

# Extract body (everything after second ---)
BODY=$(awk '/^---$/{n++; next} n>=2' "$ARTICLE_FILE")

# Build JSON payload
JSON_BODY=$(python3 -c "
import json, sys
body = sys.stdin.read()
tags = '$TAGS'.split(', ')
article = {
    'article': {
        'title': '$TITLE',
        'published': True,
        'body_markdown': body,
        'tags': tags[:4],
    }
}
if '$CANONICAL':
    article['article']['canonical_url'] = '$CANONICAL'
print(json.dumps(article))
" <<< "$BODY")

echo "Publishing: $TITLE"
echo "Tags: $TAGS"

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST https://dev.to/api/articles \
    -H "api-key: $DEVTO_KEY" \
    -H "Content-Type: application/json" \
    -d "$JSON_BODY")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY_RESP=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "201" ]; then
    URL=$(echo "$BODY_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))" 2>/dev/null)
    echo "Published successfully!"
    echo "URL: $URL"
else
    echo "Error (HTTP $HTTP_CODE):"
    echo "$BODY_RESP" | python3 -m json.tool 2>/dev/null || echo "$BODY_RESP"
fi
