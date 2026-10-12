"""
Hot-reload module for Kai 9000 Python plugins.
Uses watchdog to watch plugin files and reload them on change.
"""
import os
import sys
import importlib
import threading
import time
from pathlib import Path
from typing import Dict, Set, Callable, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    HOTRELOAD_AVAILABLE = True
except ImportError:
    HOTRELOAD_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object
    FileModifiedEvent = object

# Plugin directory
PLUGIN_DIR = Path(__file__).parent
PLUGIN_FILES = {
    "plugin_alert.py",
    "plugin_backup.py",
    "plugin_daemon.py",
    "plugin_file_organizer.py",
    "plugin_git_sync.py",
    "plugin_log_rotation.py",
    "plugin_notifications.py",
    "plugin_obsidian.py",
    "plugin_self_healing.py",
    "plugin_storage.py",
    "plugin_tui.py",
    "plugin_hotreload.py",  # self
}


class PluginReloader(FileSystemEventHandler):
    """Watches plugin files and triggers reload on modification."""
    
    def __init__(self, callback: Callable[[], None], debounce_ms: int = 500):
        self.callback = callback
        self.debounce_ms = debounce_ms
        self._last_event: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def on_modified(self, event):
        if not HOTRELOAD_AVAILABLE:
            return
        if not isinstance(event, FileModifiedEvent):
            return
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        if filepath.name not in PLUGIN_FILES:
            return
        
        # Debounce
        now = time.time() * 1000
        with self._lock:
            last = self._last_event.get(filepath.name, 0)
            if now - last < self.debounce_ms:
                return
            self._last_event[filepath.name] = now
        
        print(f"[HOTRELOAD] Detected change in {filepath.name}, triggering reload...")
        self.callback()


def reload_plugin(module_name: str) -> bool:
    """Reload a single plugin module and re-register its tools."""
    try:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
        return True
    except Exception as e:
        print(f"[HOTRELOAD] Failed to reload {module_name}: {e}")
        return False


def reload_all_plugins() -> Dict[str, bool]:
    """Reload all known plugin modules."""
    results = {}
    for plugin_file in PLUGIN_FILES:
        module_name = plugin_file[:-3]  # strip .py
        if module_name == "plugin_hotreload":
            continue  # skip self to avoid recursion
        results[module_name] = reload_plugin(module_name)
    return results


def start_hot_reload(callback: Optional[Callable[[], None]] = None):
    """
    Start the hot-reload watcher.
    Returns the Observer instance (call .stop() to shutdown).
    """
    if not HOTRELOAD_AVAILABLE:
        print("[HOTRELOAD] watchdog not available, skipping")
        return None
    
    if callback is None:
        callback = reload_all_plugins
    
    event_handler = PluginReloader(callback)
    observer = Observer()
    observer.schedule(event_handler, str(PLUGIN_DIR), recursive=False)
    observer.start()
    
    print(f"[HOTRELOAD] Watching {PLUGIN_DIR} for plugin changes")
    return observer


def stop_hot_reload(observer):
    """Stop the hot-reload watcher."""
    if observer is None:
        return
    observer.stop()
    observer.join()
    print("[HOTRELOAD] Stopped")


# Auto-register if imported as part of plugin system
if __name__ == "__main__":
    # Test mode
    obs = start_hot_reload()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_hot_reload(obs)
