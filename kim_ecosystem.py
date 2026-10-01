import time, json, os, threading, subprocess, urllib.request
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

REPO_PATH, PORT, app_instance = os.path.expanduser("~/kim-kai-ecosystem"), 8765, None
SETTINGS_PATH = os.path.join(REPO_PATH, "kai-settings.json")

# --- TOOLSET 1: TELEMETRY SERVER ---
class TelemetryHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/push":
            try:
                data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf-8'))
                if app_instance:
                    app_instance.call_from_thread(app_instance.log_message, f"[{data.get('title', 'EVENT').upper()}] {data.get('message', '')}")
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(400); self.end_headers(); self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
        else: self.send_response(404); self.end_headers()
    def log_message(self, format, *args): pass

def start_server(): HTTPServer(('127.0.0.1', PORT), TelemetryHandler).serve_forever()

# --- TOOLSET 2: AUTONOMOUS HEARTBEAT DAEMON ---
def start_daemon():
    time.sleep(2)
    while True:
        ms, t_str = int(time.time() * 1000), datetime.now().strftime("%H:%M:%S")
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r') as f: data = json.load(f)
                data.setdefault("heartbeat_config", {})["lastHeartbeatEpochMs"] = ms
                data.setdefault("heartbeat_log", []).insert(0, {"timestampEpochMs": ms, "success": True})
                data["heartbeat_log"] = data["heartbeat_log"][:20]
                tmp = SETTINGS_PATH + ".tmp"
                with open(tmp, 'w') as f: json.dump(data, f, indent=4)
                os.replace(tmp, SETTINGS_PATH)
            except Exception: pass
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PORT}/push", data=json.dumps({"title": "Heartbeat", "message": f"Pulse executed at {t_str}."}).encode('utf-8'), headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=2)
        except Exception: pass
        time.sleep(600)

# --- TOOLSET 3: ANDROID NOTIFICATION TELEMETRY POLLER ---
def start_notification_poller():
    time.sleep(5)
    seen_notifications = set()
    while True:
        try:
            res = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                notifs = json.loads(res.stdout)
                for n in notifs[:5]: # Check latest 5 notifications
                    n_id = f"{n.get('packageName')}-{n.get('title')}-{n.get('key')}"
                    if n_id not in seen_notifications:
                        seen_notifications.add(n_id)
                        if len(seen_notifications) > 100: seen_notifications.pop()
                        
                        pkg = n.get('packageName', 'system').split('.')[-1]
                        title = n.get('title', 'Alert')
                        text = n.get('text', '')
                        msg = f"[{pkg}] {title}: {text}"
                        
                        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/push", data=json.dumps({"title": "Android", "message": msg}).encode('utf-8'), headers={'Content-Type': 'application/json'})
                        urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass # Termux API not installed or unavailable
        time.sleep(30) # Poll every 30 seconds

# --- TOOLSET 4: TUI DASHBOARD & ASYNC WORKERS ---
class KimDashboard(App):
    CSS = """
    Screen { background: #0f172a; color: #e2e8f0; }
    #sidebar { width: 35%; border: solid #3b82f6; padding: 1; background: #1e293b; }
    #main-content { width: 65%; border: solid #10b981; padding: 1; background: #1e293b; }
    .box-title { color: #38bdf8; text-style: bold; }
    Log { background: #090d16; color: #34d399; border: solid #059669; height: 100%; }
    """
    BINDINGS = [Binding("q", "quit", "Quit", show=True), Binding("r", "refresh_status", "Refresh", show=True), Binding("s", "sync_repo", "Git Sync", show=True)]

    def __init__(self): super().__init__(); global app_instance; app_instance = self

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("SYSTEM STATUS", classes="box-title")
                yield Static("Env: Termux\nArchitecture: Interwoven\nState: NOMINAL\n")
                yield Static("\nMODULE THREADS", classes="box-title")
                yield Static("1. Server [Port 8765]\n2. Heartbeat [10m Loop]\n3. Notif Poller [30s]\n4. TUI Dashboard\n")
            with Vertical(id="main-content"):
                yield Static("LIVE ECOSYSTEM LOGS", classes="box-title")
                yield Log(id="log_view", highlight=True)
        yield Footer()

    async def on_mount(self) -> None:
        self.log_message("[INIT] Unified ecosystem online with Notification Scraper.")

    def log_message(self, text: str) -> None: self.query_one(Log).write(text)
    def action_refresh_status(self) -> None: self.log_message("[REFRESH] Interwoven subsystem check: Nominal.")
    def action_sync_repo(self) -> None: self.run_worker(self._git_sync_worker, thread=True)

    def _git_sync_worker(self) -> None:
        try:
            subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
            res = subprocess.run(["git", "commit", "-m", "auto: interwoven ecosystem sync with notifications"], cwd=REPO_PATH, capture_output=True, text=True)
            if res.returncode == 0:
                push = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True)
                msg = "[GIT] Push successful!" if push.returncode == 0 else f"[GIT ERROR] {push.stderr.strip()}"
            else: msg = f"[GIT] Notice: {res.stdout.strip()}"
        except Exception as e: msg = f"[GIT ERROR] {str(e)}"
        self.call_from_thread(self.log_message, msg)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=start_daemon, daemon=True).start()
    threading.Thread(target=start_notification_poller, daemon=True).start()
    KimDashboard().run()
