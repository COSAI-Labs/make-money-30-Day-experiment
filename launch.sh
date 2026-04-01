#!/bin/bash
# Launch the full autonomous agent team in tmux
# Each role runs in its own tmux window, auto-restarts on exit
# Usage: ./launch.sh

PROJECT_DIR="/home/GerritRoskaBot/make-money-30day-challenge"
SESSION="make-money"

# Kill existing session if any
tmux kill-session -t "$SESSION" 2>/dev/null
sleep 2

# Create new session with main runner
tmux new-session -d -s "$SESSION" -n "main" "bash $PROJECT_DIR/run.sh main"

# Add specialist windows (stagger starts to avoid git conflicts)
sleep 5
tmux new-window -t "$SESSION" -n "builder" "bash $PROJECT_DIR/run.sh builder"

sleep 5
tmux new-window -t "$SESSION" -n "growth" "bash $PROJECT_DIR/run.sh growth"

echo "Launched $SESSION with 3 parallel runners:"
echo "  - main:    sets up crons, builds, coordinates"
echo "  - builder: executes top priorities from research"
echo "  - growth:  distribution, submissions, outreach"
echo ""
echo "Monitor: tmux attach -t $SESSION"
echo "Logs:    tail -f $PROJECT_DIR/logs/runner-*.log"
tmux ls
