import os
import sys
import importlib.util
import time
from typing import Callable, Dict, Any

# Central internal registry for Kai 9000
KAI_NATIVE_REGISTRY: Dict[str, Dict[str, Any]] = {}

def kai_tool(name: str, description: str):
    """The universal decorator for Kai plugins."""
    def decorator(func: Callable):
        KAI_NATIVE_REGISTRY[name] = {
            "function": func,
            "description": description
        }
        return func
    return decorator

# Inject the decorator into the builtins so plugins can use it without complex imports
import builtins
builtins.kai_tool = kai_tool

class KaiCoreWatcher:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = os.path.join(os.path.dirname(__file__), plugin_dir)
        
    def ingest_plugins(self):
        """Scans the plugins directory and hot-loads all Python modules."""
        print(f"[KAI CORE] Scanning {self.plugin_dir} for native tools...")
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            
        loaded_count = 0
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(self.plugin_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    loaded_count += 1
                except Exception as e:
                    print(f"[KAI CORE ERROR] Failed to load plugin {filename}: {str(e)}")
                    
        print(f"[KAI CORE] Ingestion complete. {loaded_count} modules hot-loaded.")
        print(f"[KAI CORE] Active Native Tools: {list(KAI_NATIVE_REGISTRY.keys())}\n")

    def execute(self, tool_name: str, *args, **kwargs) -> Any:
        if tool_name not in KAI_NATIVE_REGISTRY:
            return {"error": f"Tool '{tool_name}' not recognized."}
        print(f"[EXECUTE] Dispatching {tool_name}...")
        return KAI_NATIVE_REGISTRY[tool_name]["function"](*args, **kwargs)

if __name__ == "__main__":
    watcher = KaiCoreWatcher()
    watcher.ingest_plugins()
    
    # Keeps the core alive, watching for internal event triggers
    print("Kai Core is now idling and listening for task assignments.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Kai Core.")
