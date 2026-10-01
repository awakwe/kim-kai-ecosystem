#!/bin/sh
echo "=========================================="
echo "    KAI 9000 // NATIVE CORE BOOT          "
echo "=========================================="

cd ~/kim-kai-ecosystem || exit 1

# Terminate any lingering legacy processes
pkill -f "kim_server.py"
pkill -f "kim_daemon.py"
pkill -f "kim_alert.py"
pkill -f "kai_core_loader.py"

# Initialize the new dynamic core
echo "[BOOT] Initializing Kai Core Watcher..."
python kai_core_loader.py
