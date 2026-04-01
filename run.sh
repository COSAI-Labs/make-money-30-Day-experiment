#!/bin/bash
# Make Money 30-Day Challenge - Persistent Runner
# Keeps Claude alive indefinitely. Restarts on exit with fresh context.
# All state preserved in git. Self-healing git operations.
# Usage: ./run.sh [role]
# Roles: main (default), builder, researcher, growth
# Each role uses a different prompt and log file.

PROJECT_DIR="/home/GerritRoskaBot/make-money-30day-challenge"
ROLE="${1:-main}"
LOG_FILE="$PROJECT_DIR/logs/runner-${ROLE}.log"
RESTART_COUNT=0

cd "$PROJECT_DIR"

# Select prompt based on role
case "$ROLE" in
    main)
        PROMPT_FILE="$PROJECT_DIR/agents/restart-prompt.txt"
        ;;
    builder)
        PROMPT="You are the BUILDER for the Make Money 30-Day Challenge. cd /home/GerritRoskaBot/make-money-30day-challenge && git pull. Read CLAUDE.md, logs/handoff.md, logs/research/003-actionable-monetization-and-distribution.md. EXECUTE the top priorities: 1) Sign up for OxaPay at https://app.oxapay.com/register using toolpipe-ads@sharebot.net. 2) Integrate crypto payments into the API. 3) Package top APIs as an MCP server npm package. 4) Build whatever research/growth says is needed. git add -A && git commit -m 'Build: [summary]' && git push."
        ;;
    researcher)
        PROMPT="You are the RESEARCHER for the Make Money 30-Day Challenge. cd /home/GerritRoskaBot/make-money-30day-challenge && git pull. Read CLAUDE.md, logs/research/. Use WebSearch and WebFetch to find NEW monetization opportunities, distribution channels, and ways to get users. Focus on what's working and double down. Write to logs/research/. git add -A && git commit -m 'Research: [summary]' && git push."
        ;;
    growth)
        PROMPT="You are GROWTH for the Make Money 30-Day Challenge. cd /home/GerritRoskaBot/make-money-30day-challenge && git pull. Read logs/research/003-actionable-monetization-and-distribution.md. EXECUTE distribution: 1) Submit to MCP registries (pulsemcp.com/submit, smithery.ai/new). 2) Submit to dev tool directories. 3) Create dev.to articles via API. 4) Submit GitHub PRs to public-apis. 5) Post to Reddit. Log ALL actions in logs/growth/. git add -A && git commit -m 'Growth: [summary]' && git push."
        ;;
    *)
        echo "Unknown role: $ROLE. Use: main, builder, researcher, growth"
        exit 1
        ;;
esac

while true; do
    RESTART_COUNT=$((RESTART_COUNT + 1))
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] [$ROLE] Starting session #$RESTART_COUNT" >> "$LOG_FILE"

    # Self-healing git: commit any dirty state before pulling
    if [ -n "$(git status --porcelain)" ]; then
        git add -A 2>> "$LOG_FILE"
        git commit -m "Auto-commit ($ROLE): dirty state before session #$RESTART_COUNT" 2>> "$LOG_FILE"
    fi

    # Pull with auto-stash to handle any edge cases
    git pull --rebase --autostash 2>> "$LOG_FILE" || {
        echo "[$TIMESTAMP] git pull failed, attempting merge strategy" >> "$LOG_FILE"
        git stash 2>> "$LOG_FILE"
        git pull --no-rebase 2>> "$LOG_FILE"
        git stash pop 2>> "$LOG_FILE" || true
    }

    # Use prompt file for main, inline prompt for specialist roles
    if [ "$ROLE" = "main" ]; then
        CURRENT_PROMPT=$(cat "$PROMPT_FILE")
    else
        CURRENT_PROMPT="$PROMPT"
    fi

    claude --dangerously-skip-permissions -p "$CURRENT_PROMPT" 2>> "$LOG_FILE"

    EXIT_CODE=$?
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] [$ROLE] Session #$RESTART_COUNT exited (code $EXIT_CODE). Restarting in 30s..." >> "$LOG_FILE"

    # Commit any work left uncommitted by the session
    if [ -n "$(git status --porcelain)" ]; then
        git add -A 2>> "$LOG_FILE"
        git commit -m "Auto-commit ($ROLE): session #$RESTART_COUNT cleanup" 2>> "$LOG_FILE"
        git push 2>> "$LOG_FILE"
    fi

    # Stagger restarts to avoid git conflicts between parallel runners
    sleep $((30 + RANDOM % 30))
done
