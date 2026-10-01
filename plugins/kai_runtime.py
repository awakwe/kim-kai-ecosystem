import os
import json
import time
from typing import Callable, Dict, Any
import functools

# --- 1. CORE TOOL REGISTRY ---
KAI_TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

def kai_tool(name: str, description: str):
    """Decorator to register a function as an official Kai 9000 native tool."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        KAI_TOOL_REGISTRY[name] = {
            "function": wrapper,
            "description": description
        }
        return wrapper
    return decorator

# --- 2. NATIVE TOOL DEFINITIONS ---

@kai_tool(
    name="git_sync",
    description="Stages changes, runs pre-commit audit checks, commits, and pushes to origin/main."
)
def native_git_sync(repo_path: str = "~/kim-kai-ecosystem") -> Dict[str, Any]:
    import subprocess
    path = os.path.expanduser(repo_path)
    try:
        subprocess.run(["git", "add", "."], cwd=path, check=True)
        res = subprocess.run(["git", "commit", "-m", "auto: native kai cluster sync"], cwd=path, capture_output=True, text=True)
        if res.returncode == 0:
            push = subprocess.run(["git", "push", "origin", "main"], cwd=path, capture_output=True, text=True)
            if push.returncode == 0:
                return {"status": "success", "message": "Changes committed and pushed successfully."}
            return {"status": "error", "message": push.stderr.strip()}
        out = res.stdout.strip()
        if "nothing to commit" in out:
            return {"status": "clean", "message": "Working tree clean. No sync needed."}
        return {"status": "notice", "message": out}
    except Exception as e:
        return {"status": "exception", "message": str(e)}

@kai_tool(
    name="storage_audit",
    description="Inspects sandbox volume availability and returns disk space telemetry."
)
def native_storage_audit(repo_path: str = "~/kim-kai-ecosystem", warning_threshold_mb: int = 500) -> Dict[str, Any]:
    import shutil
    path = os.path.expanduser(repo_path)
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (2**20)
        warning = free_mb < warning_threshold_mb
        return {
            "status": "warning" if warning else "nominal",
            "free_space_mb": free_mb,
            "total_space_mb": total // (2**20),
            "message": f"Storage nominal: {free_mb}MB free." if not warning else f"LOW STORAGE WARNING: {free_mb}MB remaining."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@kai_tool(
    name="poll_notifications",
    description="Scrapes recent system notifications via Termux API or native event bridge."
)
def native_poll_notifications(limit: int = 5) -> Dict[str, Any]:
    import subprocess
    try:
        res = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            notifs = json.loads(res.stdout)
            return {"status": "success", "notifications": notifs[:limit]}
        return {"status": "empty", "notifications": []}
    except Exception as e:
        return {"status": "unavailable", "message": "Termux API bridge not reachable.", "details": str(e)}

# --- 3. KAI RUNTIME DISPATCHER ---
class KaiRuntimeEngine:
    def __init__(self, settings_path: str = "~/kim-kai-ecosystem/kai-settings.json"):
        self.settings_path = os.path.expanduser(settings_path)
        self.registry = KAI_TOOL_REGISTRY

    def execute(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        if tool_name not in self.registry:
            return {"status": "error", "message": f"Tool '{tool_name}' not found in Kai registry."}
        
        print(f"[KAI RUNTIME] Executing tool: {tool_name}")
        tool_entry = self.registry[tool_name]
        try:
            result = tool_entry["function"](*args, **kwargs)
            self._log_execution(tool_name, "success", result)
            return result
        except Exception as e:
            err_res = {"status": "exception", "message": str(e)}
            self._log_execution(tool_name, "failed", err_res)
            return err_res

    def _log_execution(self, tool_name: str, state: str, result: Dict[str, Any]):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                data.setdefault("execution_log", []).insert(0, {
                    "timestampEpochMs": int(time.time() * 1000),
                    "tool": tool_name,
                    "state": state,
                    "result": result
                })
                data["execution_log"] = data["execution_log"][:50] # Keep last 50
                tmp = self.settings_path + ".tmp"
                with open(tmp, 'w') as f:
                    json.dump(data, f, indent=4)
                os.replace(tmp, self.settings_path)
            except Exception:
                pass

if __name__ == "__main__":
    engine = KaiRuntimeEngine()
    print("Kai 9000 Runtime Initialized. Registered tools:", list(engine.registry.keys()))
    
    # Test a sample audit tool execution
    audit_res = engine.execute("storage_audit")
    print("Execution Result:", json.dumps(audit_res, indent=2))
