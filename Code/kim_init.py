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
            "GCP_API_KEY": "${GCP_API_KEY}",
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
