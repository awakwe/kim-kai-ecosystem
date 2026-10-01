import os
import sys
import time
import importlib.util
import builtins
from typing import Callable, Dict, Any

KAI_NATIVE_REGISTRY: Dict[str, Dict[str, Any]] = {}
builtins.KAI_NATIVE_REGISTRY = KAI_NATIVE_REGISTRY

def kai_tool(name: str, description: str):
    def decorator(func: Callable):
        KAI_NATIVE_REGISTRY[name] = {"function": func, "description": description}
        return func
    return decorator

builtins.kai_tool = kai_tool

class KaiCoreWatcher:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = os.path.join(os.path.dirname(__file__), plugin_dir)
        
    def ingest_plugins(self):
        if not os.path.exists(self.plugin_dir): os.makedirs(self.plugin_dir)
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(self.plugin_dir, filename)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                except Exception:
                    pass

    def execute(self, tool_name: str, *args, **kwargs) -> Any:
        if tool_name in KAI_NATIVE_REGISTRY:
            return KAI_NATIVE_REGISTRY[tool_name]["function"](*args, **kwargs)
        return {"error": f"Tool '{tool_name}' not found."}

if __name__ == "__main__":
    watcher = KaiCoreWatcher()
    watcher.ingest_plugins()
    
    log_path = os.path.expanduser("~/kim-kai-ecosystem/ecosystem.log")
    if os.path.exists(log_path): open(log_path, 'w').close()
    
    watcher.execute("start_server")
    watcher.execute("start_daemon")
    watcher.execute("start_self_healing")
    
    # TTY Detection Logic
    if sys.stdout.isatty():
        print("[KAI CORE] TTY attached. Initializing TUI Dashboard...")
        watcher.execute("start_tui")
    else:
        with open(log_path, "a") as f:
            f.write("[KAI CORE] Headless boot detected. Running as background daemon.\n")
        # Keep the main thread alive infinitely so background threads don't exit
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
