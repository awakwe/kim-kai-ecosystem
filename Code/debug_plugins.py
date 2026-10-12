import os
import importlib.util
import traceback
import builtins

# Mock the registry and decorator so plugins can load independently
builtins.KAI_NATIVE_REGISTRY = {}
def mock_kai_tool(name, description):
    def decorator(func):
        return func
    return decorator
builtins.kai_tool = mock_kai_tool

print("--- SCANNING PLUGINS ---")
for filename in os.listdir("plugins"):
    if filename.endswith(".py") and not filename.startswith("__"):
        try:
            spec = importlib.util.spec_from_file_location(filename[:-3], f"plugins/{filename}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"[  OK  ] {filename}")
        except Exception as e:
            print(f"[FAILED] {filename}")
            traceback.print_exc()
            print("-" * 40)
