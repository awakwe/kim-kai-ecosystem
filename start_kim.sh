#!/bin/sh
echo "=========================================="
echo "    KIM // KAI 9000 SYSTEM ORCHESTRATOR    "
echo "=========================================="

# Ensure working directory is correct
cd ~/kim-kai-ecosystem || exit 1

# Ensure pre-commit hook is executable
if [ -f ".git/hooks/pre-commit" ]; then
    chmod +x .git/hooks/pre-commit
    echo "[SECURITY] Pre-commit hook verified active."
fi

# Kill any existing background heartbeat daemons to avoid duplicates
pkill -f "kim_heartbeat.py"

# Start the background heartbeat daemon
echo "[DAEMON] Launching Kai 9000 heartbeat loop..."
python kim_heartbeat.py > heartbeat.log 2>&1 &
echo "[DAEMON] PID $! running in background. Logs -> heartbeat.log"

# Launch the interactive TUI Dashboard
echo "[UI] Booting Kim TUI Dashboard..."
python kim_dashboard.py
