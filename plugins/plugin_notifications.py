import subprocess
import json

@kai_tool(name="poll_notifications", description="Scrapes recent system notifications via Termux API.")
def poll_notifications(limit: int = 5) -> dict:
    try:
        res = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            notifs = json.loads(res.stdout)
            
            # Format the output for better readability
            formatted_notifs = []
            for n in notifs[:limit]:
                pkg = n.get('packageName', 'system').split('.')[-1]
                formatted_notifs.append(f"[{pkg}] {n.get('title', 'Alert')}: {n.get('text', '')}")
                
            return {"status": "success", "count": len(formatted_notifs), "notifications": formatted_notifs}
        return {"status": "empty", "notifications": []}
    except Exception as e:
        return {"status": "unavailable", "message": "Termux API bridge not reachable.", "details": str(e)}
