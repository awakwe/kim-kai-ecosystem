import builtins
builtins.KAI_NATIVE_REGISTRY = {}
def mock_kai_tool(name, description):
    def decorator(func):
        builtins.KAI_NATIVE_REGISTRY[name] = {"function": func, "description": description}
        return func
    return decorator
builtins.kai_tool = mock_kai_tool

import plugins.plugin_obsidian as po
from http.server import HTTPServer
import plugins.plugin_server as ps

print("Booting Foreground MCP Server...")
try:
    server = HTTPServer(('127.0.0.1', 8765), ps.MCPHandler)
    print("\n[ SUCCESS ] Server successfully bound to port 8765!")
    print("Leave this window open, open a New Session, and run your curl command.")
    server.serve_forever()
except Exception as e:
    print(f"\n[ FATAL ERROR ] Could not bind to port 8765:")
    print(str(e))
