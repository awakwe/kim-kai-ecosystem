import os
import tarfile
from datetime import datetime

@kai_tool(name="backup", description="Generates a compressed .tar.gz archive snapshot of the ecosystem workspace.")
def create_backup(repo_path: str = "~/kim-kai-ecosystem", backup_dir: str = "~/kim-kai-backups") -> dict:
    source = os.path.expanduser(repo_path)
    destination = os.path.expanduser(backup_dir)
    os.makedirs(destination, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kim_backup_{timestamp}.tar.gz"
    filepath = os.path.join(destination, filename)
    
    try:
        with tarfile.open(filepath, "w:gz") as tar:
            tar.add(source, arcname=os.path.basename(source), exclude=lambda p: "kim-backups" in p or ".git" in p)
        file_size_kb = os.path.getsize(filepath) // 1024
        return {
            "status": "success",
            "archive": filename,
            "size_kb": file_size_kb,
            "message": f"Backup created successfully: {filename} ({file_size_kb} KB)"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
