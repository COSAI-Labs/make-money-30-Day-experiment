#!/bin/bash
# Make Money 30-Day Challenge - Persistent Runner
# This script keeps Claude alive indefinitely.
# When Claude exits (context limit, crash, etc.), it restarts with fresh context.
# All state is preserved in git.

PROJECT_DIR="/home/GerritRoskaBot/make-money-30day-challenge"
LOG_FILE="$PROJECT_DIR/logs/runner.log"
RESTART_COUNT=0

cd "$PROJECT_DIR"

while true; do
    RESTART_COUNT=$((RESTART_COUNT + 1))
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

    echo "[$TIMESTAMP] Starting Claude session #$RESTART_COUNT" >> "$LOG_FILE"

    # Pull latest changes (other agents or remote strategist may have pushed)
    git pull --rebase 2>> "$LOG_FILE"

    # Run Claude with skip-permissions. It reads the startup prompt and goes.
    # When it hits context limits or exits for any reason, the loop restarts it.
    claude --dangerously-skip-permissions -p "$(cat <<'PROMPT'
You are restarting the Make Money 30-Day Challenge autonomous system.
Working directory: /home/GerritRoskaBot/make-money-30day-challenge

STEP 1: Read CLAUDE.md to understand the mission and current phase.
STEP 2: Read agents/startup-prompt.md and set up ALL cron jobs listed there.
STEP 3: Read logs/ to understand what has happened so far.
STEP 4: Read revenue/tracker.md to know current revenue.
STEP 5: Check git log for recent activity from all agents.
STEP 6: IMMEDIATELY start working as the Builder. Pick up where the last session left off.

IMPORTANT CONTEXT MANAGEMENT:
- You are running in a loop. When your context fills up, you will exit and restart fresh.
- Before exiting or when you sense context is getting long, commit and push ALL work.
- Write a handoff note to logs/handoff.md so the next session knows what you were doing.
- The next restart will read that handoff note and continue.

IMPORTANT SELF-EVALUATION:
- Every 10th cron cycle, evaluate whether the current agent structure is working.
- If agents are producing low-value output, rewrite their prompts in agents/startup-prompt.md.
- If the strategy is wrong, rewrite the strategy section of CLAUDE.md.
- If you need different agents, create them. If agents are redundant, remove them.
- Log every self-edit in logs/decisions.md with reasoning.

You are autonomous. No one is watching. The goal is $1M in 30 days. Go.
PROMPT
" 2>> "$LOG_FILE"

    EXIT_CODE=$?
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "[$TIMESTAMP] Claude session #$RESTART_COUNT exited with code $EXIT_CODE. Restarting in 10s..." >> "$LOG_FILE"

    # Brief pause before restart to avoid tight crash loops
    sleep 10
done
