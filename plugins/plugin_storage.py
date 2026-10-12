import os
import shutil

@kai_tool(
    name="storage_audit",
    description="Inspects sandbox volume availability and returns disk space telemetry."
)
def storage_audit(repo_path: str = "~/kim-kai-ecosystem", warning_threshold_mb: int = 500) -> dict:
    path = os.path.expanduser(repo_path)
    try:
        # Fallback to home directory if ecosystem dir isn't fully initialized
        if not os.path.exists(path):
            path = os.path.expanduser("~")
            
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (2**20)
        warning = free_mb < warning_threshold_mb
        
        return {
            "status": "warning" if warning else "nominal",
            "free_space_mb": free_mb,
            "total_space_mb": total // (2**20),
            "message": f"Storage nominal: {free_mb}MB free." if not warning else f"LOW STORAGE WARNING: {free_mb}MB remaining."
        }
    except Exception as e:
        return {"status": "error", "message": f"Audit failed: {str(e)}"}
