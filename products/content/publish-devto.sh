#!/bin/bash
# Publish articles to dev.to via their API
# Usage: DEVTO_API_KEY=xxx ./publish-devto.sh

if [ -z "$DEVTO_API_KEY" ]; then
  echo "Error: DEVTO_API_KEY environment variable required"
  echo "Get one at: https://dev.to/settings/extensions (API Keys section)"
  exit 1
fi

ARTICLES_DIR="$(dirname "$0")/articles"

for article in "$ARTICLES_DIR"/*.md; do
  echo "Publishing: $article"

  # Extract frontmatter fields
  title=$(grep '^title:' "$article" | sed 's/title: *"\?\(.*\)"\?/\1/' | sed 's/"$//')
  tags=$(grep '^tags:' "$article" | sed 's/tags: *//')
  canonical=$(grep '^canonical_url:' "$article" | sed 's/canonical_url: *//')

  # Extract body (everything after second ---)
  body=$(awk '/^---$/{n++}n>=2' "$article" | tail -n +2)

  # Build JSON payload
  payload=$(python3 -c "
import json, sys
print(json.dumps({
    'article': {
        'title': '''$title''',
        'body_markdown': sys.stdin.read(),
        'published': False,
        'tags': [t.strip() for t in '''$tags'''.split(',')],
        'canonical_url': '''$canonical'''
    }
}))
" <<< "$body")

  # POST to dev.to
  response=$(curl -s -X POST "https://dev.to/api/articles" \
    -H "api-key: $DEVTO_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload")

  url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url','ERROR'))" 2>/dev/null)
  echo "  Result: $url"

  sleep 3  # Rate limit: 10 per 30 seconds
done

echo "Done! Articles published as drafts. Review and publish at https://dev.to/dashboard"
