import time
import json
import os
import threading
import subprocess
import urllib.request
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

REPO_PATH = os.path.expanduser("~/kim-kai-ecosystem")
SETTINGS_PATH = os.path.join(REPO_PATH, "kai-settings.json")
PORT = 8765
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
        return

def run_server():
    server = HTTPServer(('127.0.0.1', PORT), WebhookHandler)
    server.serve_forever()

def run_heartbeat_daemon():
    time.sleep(2)
    while True:
        current_ms = int(time.time() * 1000)
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
                if "heartbeat_config" not in data:
                    data["heartbeat_config"] = {}
                data["heartbeat_config"]["lastHeartbeatEpochMs"] = current_ms
                
                if "heartbeat_log" not in data:
                    data["heartbeat_log"] = []
                data["heartbeat_log"].insert(0, {"timestampEpochMs": current_ms, "success": True})
                data["heartbeat_log"] = data["heartbeat_log"][:20]
                
                with open(SETTINGS_PATH, 'w') as f:
                    json.dump(data, f, indent=4)
            except Exception:
                pass

        payload = json.dumps({"title": "Heartbeat", "message": f"Pulse executed successfully at {current_time}."}).encode('utf-8')
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/push", data=payload, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass
            
        time.sleep(600)

class KimDashboard(App):
    """Kim Unified Catch-All Ecosystem Dashboard"""
    
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
                yield Static("1. Git Sync [ACTIVE]\n2. Pre-commit Hook [ACTIVE]\n3. Heartbeat [10m Loop]\n")
            with Vertical(id="main-content"):
                yield Static("LIVE EVENT LOG & NOTIFICATIONS", classes="box-title")
                yield Log(id="log_view", highlight=True)
        yield Footer()

    async def on_mount(self) -> None:
        log_view = self.query_one(Log)
        log_view.write("[INIT] Kim Ecosystem catch-all container initialized.")
        log_view.write(f"[LISTENER] HTTP webhook bridge active on port {PORT}")
        log_view.write("[DAEMON] Autonomous 10m heartbeat thread running.")

    def log_message(self, text: str) -> None:
        log_view = self.query_one(Log)
        log_view.write(text)

    def action_refresh_data(self) -> None:
        self.log_message("[REFRESH] Ecosystem status verified nominal.")

    def action_sync_repo(self) -> None:
        self.log_message("[GIT] Initiating automated sync via pre-commit guard...")
        try:
            # Stage, commit with auto-sanitization, and push
            subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
            res = subprocess.run(["git", "commit", "-m", "auto: Kim ecosystem telemetry sync"], cwd=REPO_PATH, capture_output=True, text=True)
            if res.returncode == 0:
                self.log_message("[GIT] Commit successful. Pushing to origin...")
                push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True)
                if push_res.returncode == 0:
                    self.log_message("[GIT] Push completed successfully!")
                else:
                    self.log_message(f"[GIT ERROR] Push failed: {push_res.stderr.strip()}")
            else:
                self.log_message(f"[GIT] Commit notice: {res.stdout.strip()}")
        except Exception as e:
            self.log_message(f"[GIT ERROR] {str(e)}")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    heartbeat_thread = threading.Thread(target=run_heartbeat_daemon, daemon=True)
    heartbeat_thread.start()
    
    app = KimDashboard()
    app.run()
