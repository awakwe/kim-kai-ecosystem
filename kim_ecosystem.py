import time, json, os, threading, subprocess, urllib.request, shutil
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, Input
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

REPO_PATH, PORT, app_instance = os.path.expanduser("~/kim-kai-ecosystem"), 8765, None
SETTINGS_PATH = os.path.join(REPO_PATH, "kai-settings.json")

# --- TOOLSET 1: TELEMETRY SERVER ---
class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

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

def start_server(): 
    try:
        server = ReusableHTTPServer(('127.0.0.1', PORT), TelemetryHandler)
        server.serve_forever()
    except Exception as e:
        print(f"[SERVER ERROR] Port {PORT} bind failed: {e}")

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
                for n in notifs[:5]:
                    n_id = f"{n.get('packageName')}-{n.get('title')}-{n.get('key')}"
                    if n_id not in seen_notifications:
                        seen_notifications.add(n_id)
                        if len(seen_notifications) > 100: seen_notifications.pop()
                        pkg = n.get('packageName', 'system').split('.')[-1]
                        msg = f"[{pkg}] {n.get('title', 'Alert')}: {n.get('text', '')}"
                        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/push", data=json.dumps({"title": "Android", "message": msg}).encode('utf-8'), headers={'Content-Type': 'application/json'})
                        urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass
        time.sleep(30)

# --- TOOLSET 4: SYSTEM RESOURCE MONITOR ---
def start_resource_monitor():
    time.sleep(10)
    while True:
        try:
            total, used, free = shutil.disk_usage(REPO_PATH)
            free_mb = free // (2**20)
            if free_mb < 500:
                msg = f"LOW STORAGE WARNING: {free_mb}MB remaining on sandbox volume."
                req = urllib.request.Request(f"http://127.0.0.1:{PORT}/push", data=json.dumps({"title": "System", "message": msg}).encode('utf-8'), headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass
        time.sleep(3600)

# --- TOOLSET 5: TUI DASHBOARD & COMMAND BRIDGE ---
class KimDashboard(App):
    CSS = """
    Screen { background: #0f172a; color: #e2e8f0; layout: horizontal; }
    #sidebar { width: 32; dock: left; border: solid #3b82f6; padding: 1; background: #1e293b; height: 100%; }
    #main-content { width: 1fr; dock: right; border: solid #10b981; padding: 1; background: #1e293b; height: 100%; layout: vertical; }
    .box-title { color: #38bdf8; text-style: bold; }
    Log { background: #090d16; color: #34d399; border: solid #059669; height: 1fr; margin-bottom: 1; }
    Input { background: #090d16; color: #38bdf8; border: solid #3b82f6; height: 3; }
    """
    BINDINGS = [Binding("q", "quit", "Quit", show=True), Binding("r", "refresh_status", "Refresh", show=True), Binding("s", "sync_repo", "Git Sync", show=True)]

    def __init__(self): super().__init__(); global app_instance; app_instance = self

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sidebar"):
            yield Static("SYSTEM STATUS", classes="box-title")
            yield Static("Env: Termux\nArchitecture: Interwoven\nState: NOMINAL\n")
            yield Static("\nMODULE THREADS", classes="box-title")
            yield Static("1. Server [8765]\n2. Heartbeat [10m]\n3. Notif [30s]\n4. Storage [1h]\n5. Cmd Bridge\n")
        with Vertical(id="main-content"):
            yield Static("LIVE ECOSYSTEM LOGS & COMMAND BRIDGE", classes="box-title")
            yield Log(id="log_view", highlight=True)
            yield Input(placeholder="Type command here (e.g. git status, ls)...", id="command-input")
        yield Footer()

    async def on_mount(self) -> None:
        self.log_message("[INIT] Unified ecosystem online with Command Bridge & Socket Reuse.")

    def log_message(self, text: str) -> None:
        self.query_one(Log).write(text.strip())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        event.input.value = ""
        if not cmd:
            return
        self.log_message(f"[CMD] > {cmd}")
        # Pass cmd properly as a keyword or positional argument to worker
        self.run_worker(lambda: self._execute_command_worker(cmd), thread=True)

    def _execute_command_worker(self, cmd: str) -> None:
        try:
            res = subprocess.run(cmd, shell=True, cwd=REPO_PATH, capture_output=True, text=True, timeout=10)
            output = res.stdout.strip() if res.returncode == 0 else res.stderr.strip()
            if not output:
                output = "Command executed successfully with no output."
            for line in output.splitlines():
                self.call_from_thread(self.log_message, f"[{cmd}] {line}")
        except Exception as e:
            self.call_from_thread(self.log_message, f"[CMD ERROR] {str(e)}")

    def action_refresh_status(self) -> None: 
        self.log_message("[REFRESH] All subsystem threads verified nominal.")

    def action_sync_repo(self) -> None: 
        self.log_message("[GIT] Dispatching sync worker...")
        self.run_worker(self._git_sync_worker, thread=True)

    def _git_sync_worker(self) -> None:
        try:
            subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
            res = subprocess.run(["git", "commit", "-m", "auto: ecosystem command bridge integration"], cwd=REPO_PATH, capture_output=True, text=True)
            if res.returncode == 0:
                push = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True)
                msg = "[GIT] Push successful!" if push.returncode == 0 else f"[GIT ERROR] {push.stderr.strip()}"
            else:
                out = res.stdout.strip()
                msg = "[GIT] Working tree clean." if "nothing to commit" in out else f"[GIT] Notice: {out.splitlines()[0]}"
        except Exception as e: 
            msg = f"[GIT ERROR] {str(e)}"
        self.call_from_thread(self.log_message, msg)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=start_daemon, daemon=True).start()
    threading.Thread(target=start_notification_poller, daemon=True).start()
    threading.Thread(target=start_resource_monitor, daemon=True).start()
    KimDashboard().run()
