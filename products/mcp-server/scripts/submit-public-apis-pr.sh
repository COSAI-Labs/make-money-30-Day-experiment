#!/bin/bash
# Script to submit ToolPipe to public-apis/public-apis
# Run this after GitHub API rate limit resets (check: curl -s -H "Authorization: token $(gh auth token)" https://api.github.com/rate_limit | jq .rate)

set -e

WORK_DIR="/tmp/public-apis-pr"
BRANCH="add-toolpipe-api"

echo "=== Step 1: Check rate limit ==="
REMAINING=$(curl -s -H "Authorization: token $(gh auth token)" https://api.github.com/rate_limit | python3 -c "import sys,json; print(json.load(sys.stdin)['rate']['remaining'])")
echo "Rate limit remaining: $REMAINING"
if [ "$REMAINING" -lt 10 ]; then
    echo "ERROR: Not enough API calls remaining ($REMAINING). Wait for reset."
    exit 1
fi

echo "=== Step 2: Fork the repo ==="
gh repo fork public-apis/public-apis --clone=false 2>/dev/null || echo "Fork may already exist, continuing..."
sleep 5  # Give GitHub time to create the fork

echo "=== Step 3: Clone the fork ==="
rm -rf "$WORK_DIR"
git clone --depth=1 https://github.com/Aldric-Core/public-apis.git "$WORK_DIR"
cd "$WORK_DIR"

echo "=== Step 4: Create branch ==="
git checkout -b "$BRANCH"

echo "=== Step 5: Add ToolPipe entry ==="
# The public-apis README uses this format in a markdown table:
# | API | Description | Auth | HTTPS | CORS | Link |
# Find the Development section and add our entry alphabetically

# Find the line with "Development" section header and the table
# We need to add ToolPipe in alphabetical order in the Development section
python3 << 'PYEOF'
import re

with open("README.md", "r") as f:
    content = f.read()

# The entry to add
new_entry = "| [ToolPipe](https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/api-service) | 238+ free developer utility APIs (QR codes, JSON tools, hash generation, UUID, DNS, WHOIS, PDF, text analysis, and more) | No | Yes | Yes |"

# Find the Development section
# Look for "### Development" or "## Development" header
dev_pattern = r'(#{2,3}\s+Development\s*\n)'
match = re.search(dev_pattern, content)

if not match:
    print("ERROR: Could not find Development section")
    # Try to find what sections exist
    sections = re.findall(r'^#{2,3}\s+(.+)$', content, re.MULTILINE)
    print(f"Available sections: {sections[:20]}")
    exit(1)

# Find the table in the Development section
dev_start = match.end()
# Find the next section header
next_section = re.search(r'\n#{2,3}\s+', content[dev_start:])
if next_section:
    dev_end = dev_start + next_section.start()
else:
    dev_end = len(content)

dev_section = content[dev_start:dev_end]

# Find all table rows and insert alphabetically
lines = dev_section.split('\n')
inserted = False
new_lines = []

for i, line in enumerate(lines):
    if line.startswith('|') and not line.startswith('| API') and not line.startswith('|---'):
        # Extract API name for alphabetical comparison
        api_match = re.match(r'\|\s*\[([^\]]+)\]', line)
        if api_match:
            api_name = api_match.group(1).lower()
            if not inserted and api_name > 'toolpipe':
                new_lines.append(new_entry)
                inserted = True
    new_lines.append(line)

if not inserted:
    # Add at the end of the table (before the empty line after table)
    # Find last table row
    for i in range(len(new_lines) - 1, -1, -1):
        if new_lines[i].startswith('|'):
            new_lines.insert(i + 1, new_entry)
            inserted = True
            break

if not inserted:
    print("ERROR: Could not find where to insert the entry")
    exit(1)

new_dev_section = '\n'.join(new_lines)
new_content = content[:dev_start] + new_dev_section + content[dev_end:]

with open("README.md", "w") as f:
    f.write(new_content)

print("SUCCESS: ToolPipe entry added to Development section")
PYEOF

echo "=== Step 6: Commit and push ==="
git add README.md
git commit -m "Add ToolPipe API to Development section

ToolPipe provides 238+ free developer utility APIs including QR codes,
JSON tools, hash generation, UUID, DNS, WHOIS, PDF generation, text
analysis, image processing, and more. No authentication required."

git push origin "$BRANCH"

echo "=== Step 7: Create PR ==="
gh pr create \
    --repo public-apis/public-apis \
    --head "Aldric-Core:$BRANCH" \
    --title "Add ToolPipe API to Development section" \
    --body "$(cat <<'EOF'
## Add ToolPipe API

| Field | Value |
|-------|-------|
| API Name | ToolPipe |
| Description | 238+ free developer utility APIs (QR codes, JSON tools, hash generation, UUID, DNS, WHOIS, PDF, text analysis, and more) |
| Auth | No |
| HTTPS | Yes |
| CORS | Yes |
| Link | https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/api-service |

ToolPipe offers a comprehensive suite of free developer utilities accessible via REST API. Categories include encoding/decoding, cryptography, network tools, text processing, data generation, and more.

All endpoints are free to use with no API key required.
EOF
)"

echo "=== Done! PR created ==="
