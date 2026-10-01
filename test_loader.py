from kai_core_loader import KaiCoreWatcher

watcher = KaiCoreWatcher()
watcher.ingest_plugins()

print("--- TESTING HOT-LOADED PLUGINS ---")
backup_result = watcher.execute("backup")
print("Backup Output:", backup_result)

sync_result = watcher.execute("git_sync")
print("Git Sync Output:", sync_result)
