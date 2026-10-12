#!/usr/bin/env python3
"""
Kim 🌟 & Kai 9000 TUI Dashboard Control Center
Target: Termux / Python 3.10+ (Pixel 9a)
Author: Kim 🌟 for Uwakwe Omegbu
"""

import sqlite3
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Horizontal, Vertical

KIM_DIR = Path.home() / ".local" / "share" / "kim"
DB_PATH = KIM_DIR / "kim_state.db"

class KimTUIDashboard(App):
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #cba6f7;
    }
    Header {
        background: #313244;
        color: #f5e0dc;
    }
    Footer {
        background: #313244;
        color: #f5e0dc;
    }
    .panel {
        border: solid #b4befe;
        padding: 1;
        margin: 1;
        background: #181825;
        width: 50%;
    }
    .title {
        text-style: bold;
        color: #fab387;
        margin-bottom: 1;
    }
    DataTable {
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(classes="panel"):
                yield Static("📋 Task Registry Queue", classes="title")
                yield DataTable(id="task_table")
            with Vertical(classes="panel"):
                yield Static("💓 Live Telemetry Feed", classes="title")
                yield DataTable(id="telemetry_table")
        yield Footer()

    def on_mount(self) -> None:
        task_table = self.query_one("#task_table", DataTable)
        task_table.add_columns("ID", "Command", "Status")
        
        telemetry_table = self.query_one("#telemetry_table", DataTable)
        telemetry_table.add_columns("ID", "Timestamp", "Status")
        
        self.refresh_data()
        self.set_interval(2.0, self.refresh_data)

    def refresh_data(self):
        if not DB_PATH.exists():
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Update Tasks
            task_table = self.query_one("#task_table", DataTable)
            task_table.clear()
            cursor.execute("SELECT id, command, status FROM task_registry ORDER BY id DESC LIMIT 15")
            for row in cursor.fetchall():
                task_table.add_row(str(row[0]), str(row[1]), str(row[2]))
                
            # Update Telemetry
            telemetry_table = self.query_one("#telemetry_table", DataTable)
            telemetry_table.clear()
            cursor.execute("SELECT id, timestamp, status FROM heartbeat_telemetry ORDER BY id DESC LIMIT 15")
            for row in cursor.fetchall():
                telemetry_table.add_row(str(row[0]), str(row[1]), str(row[2]))
                
            conn.close()
        except Exception as e:
            pass

if __name__ == "__main__":
    app = KimTUIDashboard()
    app.run()
