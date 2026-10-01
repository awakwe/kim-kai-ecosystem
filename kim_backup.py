import os
import tarfile
import json
import urllib.request
from datetime import datetime

REPO_PATH = os.path.expanduser("~/kim-kai-ecosystem")
BACKUP_DIR = os.path.expanduser("~/kim-kai-backups")
WEBHOOK_URL = "http://127.0.0.1:8765/push"

def notify(title, message):
    try:
        payload = json.dumps({"title": title, "message": message}).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def create_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"kim_backup_{timestamp}.tar.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    print(f"[BACKUP] Creating archive of {REPO_PATH}...")
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(REPO_PATH, arcname=os.path.basename(REPO_PATH), exclude=lambda path: "kim-backups" in path or ".git" in path)
        
        file_size_kb = os.path.getsize(backup_path) // 1024
        msg = f"Backup created successfully: {backup_filename} ({file_size_kb} KB)"
        print(f"[BACKUP] {msg}")
        notify("Backup", msg)
    except Exception as e:
        err_msg = f"Backup failed: {str(e)}"
        print(f"[BACKUP ERROR] {err_msg}")
        notify("Backup Error", err_msg)

if __name__ == "__main__":
    create_backup()
