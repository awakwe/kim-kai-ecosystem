import json
import threading
import os
import builtins
import inspect
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8766
LOG_FILE = os.path.expanduser("~/kim-kai-ecosystem/ecosystem.log")
global_server_instance = None  # Track the instance so we can kill it

def build_tool_schema(func):
    sig = inspect.signature(func)
    schema = {"type": "object", "properties": {}, "required": []}
    type_map = {int: "integer", float: "number", bool: "boolean", dict: "object", list: "array", str: "string"}
    
    for name, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD): continue
        schema["properties"][name] = {"type": type_map.get(param.annotation, "string"), "description": f"Parameter: {name}"}
        if param.default == inspect.Parameter.empty: schema["required"].append(name)
    return schema

class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            payload = json.loads(self.rfile.read(content_length).decode('utf-8'))
            
            if self.path == '/push':
                self.handle_webhook(payload)
                return
            if payload.get("jsonrpc") == "2.0":
                response = self.handle_mcp_request(payload)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            self.send_error(400, "Bad Request")
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")

    def handle_webhook(self, payload):
        title, message = payload.get("title", "Webhook"), payload.get("message", "System event.")
        with open(LOG_FILE, "a") as f: f.write(f"[SERVER] [{title}] {message}\n")
        if "error" in title.lower() or "warning" in title.lower():
            registry = getattr(builtins, 'KAI_NATIVE_REGISTRY', {})
            if "physical_alert" in registry: registry["physical_alert"]["function"](title=title, message=message, level="warning")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')

    def handle_mcp_request(self, payload):
        req_id, method, params = payload.get("id"), payload.get("method"), payload.get("params", {})
        registry = getattr(builtins, 'KAI_NATIVE_REGISTRY', {})
        
        if method == "tools/list":
            tools = [{"name": n, "description": d.get("description", ""), "inputSchema": build_tool_schema(d.get("function"))} for n, d in registry.items() if d.get("function")]
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
        elif method == "tools/call":
            tool_name, args = params.get("name"), params.get("arguments", {})
            if tool_name in registry:
                try: return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(registry[tool_name]["function"](**args))}]}}
                except Exception as e: return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Tool not found"}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

    def log_message(self, format, *args): pass

def server_worker():
    global global_server_instance
    try:
        global_server_instance = HTTPServer(('127.0.0.1', PORT), MCPHandler)
        with open(LOG_FILE, "a") as f: f.write(f"[SERVER] Strict MCP Sentinel active on port {PORT}\n")
        global_server_instance.serve_forever()
    except Exception as e:
        pass

@kai_tool(name="start_server", description="Starts the background strict MCP listener.")
def start_server() -> dict:
    t = threading.Thread(target=server_worker, daemon=True)
    t.start()
    return {"status": "success", "message": f"MCP Server active."}

@kai_tool(name="crash_server", description="Simulates a fatal server thread crash for testing the watchdog.")
def crash_server() -> dict:
    global global_server_instance
    if global_server_instance:
        # We must shut it down from a separate thread to avoid deadlocking the active HTTP request
        def poison_pill():
            global_server_instance.shutdown()
            global_server_instance.server_close()
            with open(LOG_FILE, "a") as f: f.write(f"[CHAOS] Server thread fatally terminated by operator.\n")
        threading.Thread(target=poison_pill, daemon=True).start()
        return {"status": "success", "message": "Simulated fatal crash. Server offline."}
    return {"status": "error", "message": "Server not running."}
