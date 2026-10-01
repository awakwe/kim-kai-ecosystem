import os, subprocess
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, Input
from textual.containers import Vertical
from textual.binding import Binding

LOG_FILE = os.path.expanduser("~/kim-kai-ecosystem/ecosystem.log")

class KimTUI(App):
    CSS = """
    Screen { background: #0f172a; color: #e2e8f0; }
    Log { background: #090d16; color: #34d399; border: solid #059669; height: 1fr; margin-bottom: 1; }
    Input { background: #090d16; color: #38bdf8; border: solid #3b82f6; height: 3; }
    """
    BINDINGS = [Binding("q", "quit", "Quit", show=True), Binding("r", "refresh", "Refresh Logs", show=True)]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Log(id="log_view", highlight=True)
            yield Input(placeholder="Type shell command...", id="cmd")
        yield Footer()

    async def on_mount(self) -> None:
        self.action_refresh()

    def action_refresh(self) -> None:
        log_view = self.query_one(Log)
        log_view.clear()
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                for line in f.readlines()[-30:]: log_view.write(line.strip())
        else:
            log_view.write("[INFO] Waiting for telemetry events...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd, event.input.value = event.value.strip(), ""
        if not cmd: return
        self.run_worker(lambda: self._run_cmd(cmd), thread=True)

    def _run_cmd(self, cmd: str) -> None:
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            out = res.stdout.strip() or res.stderr.strip() or "Done."
            for line in out.splitlines():
                self.call_from_thread(self.query_one(Log).write, f"[{cmd}] {line}")
        except Exception as e:
            self.call_from_thread(self.query_one(Log).write, f"[ERROR] {str(e)}")

if __name__ == "__main__":
    KimTUI().run()
