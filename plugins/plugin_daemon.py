import threading
import time
import os
import builtins

def heartbeat_worker():
    log_file = os.path.expanduser("~/kim-kai-ecosystem/ecosystem.log")
    tick_count = 0
    while True:
        registry = getattr(builtins, 'KAI_NATIVE_REGISTRY', {})
        tick_count += 1
        
        try:
            with open(log_file, "a") as f:
                f.write(f"[DAEMON] Vanguard Heartbeat Tick: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            # Storage Check
            if "storage_audit" in registry:
                res = registry["storage_audit"]["function"]()
                if res.get("status") == "warning":
                    with open(log_file, "a") as f:
                        f.write(f"[DAEMON WARNING] {res.get('message')}\n")
                    if "physical_alert" in registry:
                        registry["physical_alert"]["function"](
                            title="Low Storage", 
                            message=res.get("message"), 
                            level="warning"
                        )
                        
            # Execute log rotation check every 10 ticks (10 minutes) to avoid disk I/O spam
            if tick_count % 10 == 0 and "rotate_logs" in registry:
                registry["rotate_logs"]["function"]()
                
        except Exception:
            pass
        time.sleep(60)

@kai_tool(name="start_daemon", description="Starts the background Vanguard heartbeat loop.")
def start_daemon() -> dict:
    t = threading.Thread(target=heartbeat_worker, name="vanguard_daemon_thread", daemon=True)
    t.start()
    return {"status": "success", "message": "Vanguard Daemon active."}
