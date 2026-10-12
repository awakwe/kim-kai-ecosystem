#!/usr/bin/env bash
python3 kim_init.py
if pgrep -f "kai_worker.py" > /dev/null; then
    echo "[+] Background task worker is already active."
else
    nohup python3 kai_worker.py > /dev/null 2>&1 &
    echo "[+] Background task worker spawned successfully."
fi
echo "✨ Kim 🌟 & Kai 9000 ecosystem is live and running!"
