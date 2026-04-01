#!/bin/bash
# Capture the current Cloudflare tunnel URL from pm2 logs
# Writes to /home/GerritRoskaBot/make-money-30day-challenge/.tunnel-url

PROJECT_DIR="/home/GerritRoskaBot/make-money-30day-challenge"
URL_FILE="${PROJECT_DIR}/.tunnel-url"
LOG_FILE="/home/GerritRoskaBot/.pm2/logs/cloudflare-tunnel-error.log"

# Extract the most recent tunnel URL
TUNNEL_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG_FILE" 2>/dev/null | tail -1)

if [ -n "$TUNNEL_URL" ]; then
    echo "$TUNNEL_URL" > "$URL_FILE"
    echo "Tunnel URL captured: $TUNNEL_URL"
else
    echo "No tunnel URL found in logs"
    exit 1
fi
