#!/bin/bash
# Make Money 30-Day Challenge - Persistent Runner
# Keeps Claude alive indefinitely. Restarts on exit with fresh context.
# All state preserved in git. Self-healing git operations.

PROJECT_DIR="/home/GerritRoskaBot/make-money-30day-challenge"
LOG_FILE="$PROJECT_DIR/logs/runner.log"
PROMPT_FILE="$PROJECT_DIR/agents/restart-prompt.txt"
RESTART_COUNT=0

# Keep the machine awake (prevent sleep/suspension)
caffeinate -d -i -s &
CAFFEINATE_PID=$!
trap "kill $CAFFEINATE_PID 2>/dev/null" EXIT

cd "$PROJECT_DIR"

while true; do
    RESTART_COUNT=$((RESTART_COUNT + 1))
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] Starting Claude session #$RESTART_COUNT" >> "$LOG_FILE"

    # Self-healing git: commit any dirty state before pulling
    if [ -n "$(git status --porcelain)" ]; then
        git add -A 2>> "$LOG_FILE"
        git commit -m "Auto-commit: dirty state before session #$RESTART_COUNT" 2>> "$LOG_FILE"
    fi

    # Pull with auto-stash to handle any edge cases
    git pull --rebase --autostash 2>> "$LOG_FILE" || {
        echo "[$TIMESTAMP] git pull failed, attempting merge strategy" >> "$LOG_FILE"
        git stash 2>> "$LOG_FILE"
        git pull --no-rebase 2>> "$LOG_FILE"
        git stash pop 2>> "$LOG_FILE" || true
    }

    PROMPT=$(cat "$PROMPT_FILE")
    claude --dangerously-skip-permissions -p "$PROMPT" 2>> "$LOG_FILE"

    EXIT_CODE=$?
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] Session #$RESTART_COUNT exited (code $EXIT_CODE). Restarting in 10s..." >> "$LOG_FILE"

    # Commit any work left uncommitted by the session
    if [ -n "$(git status --porcelain)" ]; then
        git add -A 2>> "$LOG_FILE"
        git commit -m "Auto-commit: session #$RESTART_COUNT cleanup" 2>> "$LOG_FILE"
        git push 2>> "$LOG_FILE"
    fi

    sleep 10
done
