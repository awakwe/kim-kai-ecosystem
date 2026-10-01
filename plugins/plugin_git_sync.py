import os
import subprocess

@kai_tool(name="git_sync", description="Stages changes, runs pre-commit audit checks, commits, and pushes to origin/main.")
def git_sync(repo_path: str = "~/kim-kai-ecosystem") -> dict:
    path = os.path.expanduser(repo_path)
    try:
        subprocess.run(["git", "add", "."], cwd=path, check=True)
        res = subprocess.run(["git", "commit", "-m", "auto: plugin git sync"], cwd=path, capture_output=True, text=True)
        if res.returncode == 0:
            push = subprocess.run(["git", "push", "origin", "main"], cwd=path, capture_output=True, text=True)
            if push.returncode == 0:
                return {"status": "success", "message": "Git repository successfully synced and pushed."}
            return {"status": "error", "message": f"Push failed: {push.stderr.strip()}"}
        out = res.stdout.strip()
        if "nothing to commit" in out:
            return {"status": "clean", "message": "Working tree clean. No sync needed."}
        return {"status": "notice", "message": out}
    except Exception as e:
        return {"status": "error", "message": str(e)}
