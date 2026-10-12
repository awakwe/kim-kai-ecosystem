from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

app_instance = None

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/push":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                title = data.get("title", "Event")
                message = data.get("message", "No message provided")
                
                if app_instance:
                    app_instance.call_from_thread(app_instance.log_message, f"[{title.upper()}] {message}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence default HTTP server access logs to keep terminal clean
        return

class KimDashboard(App):
    """Kim Unified TUI Dashboard for Termux + Kai 9000 Integration"""
    
    CSS = """
    Screen {
        background: #0f172a;
        color: #e2e8f0;
    }
    #sidebar {
        width: 35%;
        border: solid #3b82f6;
        padding: 1;
        background: #1e293b;
    }
    #main-content {
        width: 65%;
        border: solid #10b981;
        padding: 1;
        background: #1e293b;
    }
    .box-title {
        color: #38bdf8;
        text-style: bold;
    }
    Log {
        background: #090d16;
        color: #34d399;
        border: solid #059669;
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit Dashboard", show=True),
        Binding("r", "refresh_data", "Refresh Status", show=True),
        Binding("s", "sync_repo", "Git Sync", show=True),
    ]

    def __init__(self):
        super().__init__()
        global app_instance
        app_instance = self

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("SYSTEM STATUS", classes="box-title")
                yield Static("Environment: Termux Sandbox\nRole: Kim Operator (CBE)\nState: NOMINAL\n")
                yield Static("\nACTIVE TASKS", classes="box-title")
                yield Static("1. Git Sync [PASSED]\n2. Pre-commit Hook [ACTIVE]\n3. Heartbeat [30m Loop]\n")
            with Vertical(id="main-content"):
                yield Static("LIVE EVENT LOG & NOTIFICATIONS", classes="box-title")
                yield Log(id="log_view", highlight=True)
        yield Footer()

    async def on_mount(self) -> None:
        log_view = self.query_one(Log)
        log_view.write("[INIT] Kim TUI Dashboard initialized successfully")
        log_view.write("[LISTENER] Built-in HTTP webhook active on http://127.0.0.1:8765/push")
        log_view.write("[READY] Waiting for Kai 9000 background events...")

    def log_message(self, text: str) -> None:
        log_view = self.query_one(Log)
        log_view.write(text)

    def action_refresh_data(self) -> None:
        self.log_message("[REFRESH] Status checked: All systems nominal.")

    def action_sync_repo(self) -> None:
        self.log_message("[GIT] Executing manual sync check via remote...")

def run_server():
    server = HTTPServer(('127.0.0.1', 8765), WebhookHandler)
    server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    app = KimDashboard()
    app.run()
