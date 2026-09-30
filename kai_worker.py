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
