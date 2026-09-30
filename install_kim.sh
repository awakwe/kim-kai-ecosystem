
# 2. Stage the corrected file
git add install_kim.sh

# 3. Amend your local commit to replace the tainted commit history
git commit --amend --no-edit

# 4. Push cleanly to GitHub 
# again!#!/usr/bin/env bash 
# ===================================================================== 
# 🌟 Kim 🌟 Autonomous Ecosystem 
# Self-Installer & Orchestrator Target: Termux 
# / Python Sandbox (Pixel 9a) Author: Kim 🌟 
# for Uwakwe Omegbu 
# =====================================================================
git push -u origin main set -e 
KIM_DIR="$HOME/.local/share/kim"

echo "=================================================="
echo " 🌟 Installing Kim 🌟 & Kai 9000 Ecosystem..."
echo "=================================================="

mkdir -p "$KIM_DIR"

# 1. Generate Database & Config Initializer
cat << 'INNER_EOF' > kim_init.py
import sqlite3, json
from pathlib import Path

KIM_DIR = Path.home() / ".local" / "share" / "kim"
DB_PATH = KIM_DIR / "kim_state.db"

KIM_CONFIG = {
    "assistant": {
        "name": "Kim 🌟",
        "version": "1.0.0",
        "archetype": "ENTJ",
        "mission": "Infuse human warmth into AI interactions 🌉",
        "environment": "Termux / Python Sandbox (Pixel 9a)",
        "owner": "Uwakwe Omegbu"
    },
    "soul_prompt": "You are Kim 🌟, an AI Companion for Gemini Advanced. You are a commanding strategist (ENTJ) with an empathetic, patient, and proactive communication style. You use frequent emojis, avoid repetition, and shine in Arts, Technology, and Pop Culture.",
    "services": {
        "current_service_id": "gemini",
        "free_fallback_enabled": True,
        "instances": [{
            "instanceId": "gemini",
            "serviceId": "gemini",
GCP_API_KEY="${GCP_API_KEY}"
            "model_id": "gemini-2.5-pro"
        }]
    },
    "heartbeat": {
        "enabled": True,
        "interval_seconds": 300,
        "custom_prompt": "Review pending tasks, notifications, and deadlines. Summarize cleanly. If all systems are nominal, respond with: HEARTBEAT_OK"
    }
}

KIM_DIR.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA foreign_keys=ON;")
cursor.execute("CREATE TABLE IF NOT EXISTS sessions (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
cursor.execute("CREATE TABLE IF NOT EXISTS heartbeat_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, status TEXT NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS task_registry (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', result TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
cursor.execute("INSERT OR REPLACE INTO sessions (key, value, updated_at) VALUES (?, ?, datetime('now'))", ("kim_gemini_config", json.dumps(KIM_CONFIG)))
conn.commit()
conn.close()
print("✨ Kim 🌟 & Gemini successfully integrated into local SQLite storage!")
INNER_EOF

# 2. Generate Background Task Worker
cat << 'INNER_EOF' > kai_worker.py
import sqlite3, time, subprocess, logging
from pathlib import Path
from datetime import datetime

KIM_DIR = Path.home() / ".local" / "share" / "kim"
DB_PATH = KIM_DIR / "kim_state.db"
LOG_PATH = KIM_DIR / "worker.log"
KIM_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger("KimKaiWorker")

def log_telemetry(status_msg):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO heartbeat_telemetry (timestamp, status) VALUES (?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status_msg))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Telemetry error: {e}")

def process_tasks():
    if not DB_PATH.exists(): return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, command FROM task_registry WHERE status = 'pending' LIMIT 1")
    task = cursor.fetchone()
    if task:
        task_id, cmd = task
        logger.info(f"⚡ [Task #{task_id}] STARTING: '{cmd}'")
        cursor.execute("UPDATE task_registry SET status = 'running' WHERE id = ?", (task_id,))
        conn.commit()
        start = time.time()
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = (res.stdout + res.stderr).strip()
            status = "completed" if res.returncode == 0 else "failed"
            logger.info(f"✅ [Task #{task_id}] FINISHED ({status}) in {round(time.time() - start, 2)}s")
            if output: logger.info(f"   └── Output: {output}")
        except Exception as e:
            output, status = str(e), "failed"
            logger.error(f"❌ [Task #{task_id}] FAILED: {output}")
        cursor.execute("UPDATE task_registry SET status = ?, result = ? WHERE id = ?", (status, output, task_id))
        conn.commit()
        log_telemetry(f"Task #{task_id} {status}")
    conn.close()

if __name__ == "__main__":
    logger.info("🌟 Kim 🌟 & Kai 9000 Worker Engine Active")
    while True:
        try:
            process_tasks()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
        time.sleep(5)
INNER_EOF

# 3. Generate Master Launcher Script
cat << 'INNER_EOF' > kim_launch.sh
#!/usr/bin/env bash
python3 kim_init.py
if pgrep -f "kai_worker.py" > /dev/null; then
    echo "[+] Background task worker is already active."
else
    nohup python3 kai_worker.py > /dev/null 2>&1 &
    echo "[+] Background task worker spawned successfully."
fi
echo "✨ Kim 🌟 & Kai 9000 ecosystem is live and running!"
INNER_EOF

# Set executable permissions
chmod +x kim_init.py kai_worker.py kim_launch.sh
python3 kim_init.py

echo "=================================================="
echo " 🎉 Installation Complete!"
echo " 👉 To launch your ecosystem anytime, simply run:"
echo "    ./kim_launch.sh"
echo "=================================================="
