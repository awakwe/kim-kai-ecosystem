import time
import json
import os
from datetime import datetime

SETTINGS_PATH = os.path.expanduser("~/kim-kai-ecosystem/kai-settings.json")
WEBHOOK_URL = "http://127.0.0.1:8765/push"

def send_push(title, message):
    import urllib.request
    payload = json.dumps({"title": title, "message": message}).encode('utf-8')
    req = urllib.request.Request(
        WEBHOOK_URL, 
        data=payload, 
        headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def update_kai_heartbeat(success=True, error_msg=None):
    if not os.path.exists(SETTINGS_PATH):
        return
    
    current_ms = int(time.time() * 1000)
    
    try:
        with open(SETTINGS_PATH, 'r') as f:
            data = json.load(f)
        
        if "heartbeat_config" not in data:
            data["heartbeat_config"] = {}
        data["heartbeat_config"]["lastHeartbeatEpochMs"] = current_ms
        
        if "heartbeat_log" not in data:
            data["heartbeat_log"] = []
            
        log_entry = {
            "timestampEpochMs": current_ms,
            "success": success
        }
        if error_msg:
            log_entry["error"] = error_msg
            
        data["heartbeat_log"].insert(0, log_entry)
        data["heartbeat_log"] = data["heartbeat_log"][:20]
        
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        print(f"Failed to update settings: {e}")

if __name__ == "__main__":
    send_push("Daemon", "Kai 9000 Native Heartbeat Daemon online.")
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        update_kai_heartbeat(success=True)
        send_push("Heartbeat", f"Pulse executed successfully at {current_time}.")
        time.sleep(600)
