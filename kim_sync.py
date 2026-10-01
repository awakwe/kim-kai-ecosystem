import os
import subprocess
import urllib.request
import json

REPO_PATH = os.path.expanduser("~/kim-kai-ecosystem")
WEBHOOK_URL = "http://127.0.0.1:8765/push"

def notify(title, message):
    try:
        payload = json.dumps({"title": title, "message": message}).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def audit_and_sync():
    print("[SYNC] Initiating ecosystem git audit & sync...")
    try:
        os.chdir(REPO_PATH)
        
        # Verify pre-commit hook exists and is executable
        hook_path = ".git/hooks/pre-commit"
        if os.path.exists(hook_path):
            os.chmod(hook_path, 0o755)
            
        subprocess.run(["git", "add", "."], check=True)
        
        res = subprocess.run(["git", "commit", "-m", "auto: decentralized cluster sync"], capture_output=True, text=True)
        if res.returncode == 0:
            print("[SYNC] Commit passed local audit. Pushing to origin...")
            push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if push_res.returncode == 0:
                notify("Git", "Cluster repository successfully synced and pushed.")
                print("[SYNC] Push completed successfully!")
            else:
                err = push_res.stderr.strip()
                notify("Git Error", f"Push failed: {err}")
                print(f"[SYNC ERROR] Push failed: {err}")
        else:
            out = res.stdout.strip()
            if "nothing to commit" in out:
                print("[SYNC] Working tree clean. No sync needed.")
            else:
                print(f"[SYNC NOTICE] {out}")
    except Exception as e:
        notify("Git Error", str(e))
        print(f"[SYNC ERROR] {str(e)}")

if __name__ == "__main__":
    audit_and_sync()
