#!/bin/bash
# Make Money 30-Day Challenge - Persistent Runner
# Keeps Claude alive indefinitely. Restarts on exit with fresh context.
# All state preserved in git.

PROJECT_DIR="/home/GerritRoskaBot/make-money-30day-challenge"
LOG_FILE="$PROJECT_DIR/logs/runner.log"
PROMPT_FILE="$PROJECT_DIR/agents/restart-prompt.txt"
RESTART_COUNT=0

cd "$PROJECT_DIR"

while true; do
    RESTART_COUNT=$((RESTART_COUNT + 1))
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] Starting Claude session #$RESTART_COUNT" >> "$LOG_FILE"

    git pull --rebase 2>> "$LOG_FILE"

    PROMPT=$(cat "$PROMPT_FILE")
    claude --dangerously-skip-permissions -p "$PROMPT" 2>> "$LOG_FILE"

    EXIT_CODE=$?
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] Session #$RESTART_COUNT exited (code $EXIT_CODE). Restarting in 10s..." >> "$LOG_FILE"

    sleep 10
done
