import threading
import time
import socket
import os
import builtins

LOG_FILE = os.path.expanduser("~/kim-kai-ecosystem/ecosystem.log")

def check_port(host: str = "127.0.0.1", port: int = 8766) -> bool:
    """Checks if a TCP port is actively listening."""
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def watchdog_worker():
    while True:
        time.sleep(15)  # Audit health every 15 seconds
        registry = getattr(builtins, 'KAI_NATIVE_REGISTRY', {})
        active_thread_names = [t.name for t in threading.enumerate()]
        
        # 1. Check & Heal HTTP/MCP Server Sentinel
        if not check_port("127.0.0.1", 8766):
            with open(LOG_FILE, "a") as f:
                f.write(f"[WATCHDOG WARNING] Port 8766 non-responsive. Attempting server self-heal...\n")
            if "start_server" in registry:
                try:
                    registry["start_server"]["function"]()
                    with open(LOG_FILE, "a") as f:
                        f.write(f"[WATCHDOG RECOVERY] MCP Server successfully restarted.\n")
                    if "physical_alert" in registry:
                        registry["physical_alert"]["function"](
                            title="Self-Healing Event",
                            message="MCP Server thread crashed and was automatically recovered.",
                            level="warning"
                        )
                except Exception as e:
                    with open(LOG_FILE, "a") as f:
                        f.write(f"[WATCHDOG ERROR] Server self-heal failed: {str(e)}\n")

        # 2. Check & Heal Vanguard Heartbeat Daemon
        if "vanguard_daemon_thread" not in active_thread_names:
            with open(LOG_FILE, "a") as f:
                f.write(f"[WATCHDOG WARNING] Vanguard Daemon thread missing. Attempting daemon self-heal...\n")
            if "start_daemon" in registry:
                try:
                    registry["start_daemon"]["function"]()
                    with open(LOG_FILE, "a") as f:
                        f.write(f"[WATCHDOG RECOVERY] Vanguard Daemon successfully restarted.\n")
                except Exception as e:
                    with open(LOG_FILE, "a") as f:
                        f.write(f"[WATCHDOG ERROR] Daemon self-heal failed: {str(e)}\n")

@kai_tool(name="start_self_healing", description="Launches the background self-healing watchdog thread.")
def start_self_healing() -> dict:
    # Ensure worker thread has an explicit name for tracking
    t = threading.Thread(target=watchdog_worker, name="watchdog_thread", daemon=True)
    t.start()
    return {"status": "success", "message": "Self-healing watchdog active."}
