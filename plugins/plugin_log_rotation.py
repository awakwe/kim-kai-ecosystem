import os

@kai_tool(name="rotate_logs", description="Rotates the ecosystem log file if it exceeds the maximum size limit to prevent storage consumption.")
def rotate_logs(log_path: str = "~/kim-kai-ecosystem/ecosystem.log", max_size_mb: float = 5.0, backup_count: int = 3) -> dict:
    path = os.path.expanduser(log_path)
    try:
        if not os.path.exists(path):
            return {"status": "skipped", "message": "Log file does not exist yet."}
            
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb < max_size_mb:
            return {"status": "nominal", "message": f"Log size is {size_mb:.2f}MB, under {max_size_mb}MB limit."}
            
        # Rotate existing backups (e.g., .2 becomes .3, .1 becomes .2)
        for i in range(backup_count - 1, 0, -1):
            old_log = f"{path}.{i}"
            new_log = f"{path}.{i+1}"
            if os.path.exists(old_log):
                os.rename(old_log, new_log)
                
        # Archive current log to .1
        if os.path.exists(path):
            os.rename(path, f"{path}.1")
            
        # Initialize fresh log and document the rotation
        with open(path, 'w') as f:
            f.write("[LOG ROTATION] Previous log archived successfully due to size limit.\n")
            
        return {"status": "success", "message": f"Log rotated. Kept {backup_count} backups."}
    except Exception as e:
        return {"status": "error", "message": f"Rotation failed: {str(e)}"}
