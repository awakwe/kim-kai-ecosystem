#!/bin/sh
echo "=========================================="
echo "    KIM // FULL CLUSTER ECOSYSTEM BOOT    "
echo "=========================================="

cd ~/kim-kai-ecosystem || exit 1

# Terminate any existing micro-tool instances
pkill -f "kim_server.py"
pkill -f "kim_daemon.py"
pkill -f "kim_alert.py"

# Initialize shared log file if missing
touch ecosystem.log

# 1. Boot Server Sentinel (Port 8765)
echo "[BOOT] Starting Server Sentinel..."
python kim_server.py > server.log 2>&1 &

# 2. Boot Physical Alert Agent (Port 8766)
echo "[BOOT] Starting Physical Alert Agent..."
python kim_alert.py > alert.log 2>&1 &

# 3. Boot Heartbeat Vanguard
echo "[BOOT] Starting Heartbeat Vanguard daemon..."
python kim_daemon.py > daemon.log 2>&1 &

# Brief stabilization pause
sleep 1

# 4. Launch TUI Interface Operator (Foreground)
echo "[BOOT] Launching TUI Interface Operator..."
python kim_tui.py
