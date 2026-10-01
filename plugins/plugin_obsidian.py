import os

DEFAULT_VAULT = os.path.expanduser("~/awakwe/Week")

@kai_tool(name="read_obsidian_note", description="Reads a Markdown note from the local Obsidian vault.")
def read_obsidian_note(note_filename: str, vault_path: str = DEFAULT_VAULT) -> dict:
    path = os.path.expanduser(vault_path)
    # Ensure .md extension
    if not note_filename.endswith(".md"):
        note_filename += ".md"
        
    file_path = os.path.join(path, note_filename)
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Note '{note_filename}' not found in vault."}
        with open(file_path, "r", encoding="utf-8") as f:
            return {"status": "success", "content": f.read()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@kai_tool(name="write_obsidian_note", description="Writes or appends content to an Obsidian Markdown note.")
def write_obsidian_note(note_filename: str, content: str, mode: str = "w", vault_path: str = DEFAULT_VAULT) -> dict:
    path = os.path.expanduser(vault_path)
    os.makedirs(path, exist_ok=True)
    
    if not note_filename.endswith(".md"):
        note_filename += ".md"
        
    file_path = os.path.join(path, note_filename)
    try:
        # mode 'w' overwrites, mode 'a' appends to the bottom of the note
        with open(file_path, mode, encoding="utf-8") as f:
            if mode == "a":
                f.write("\n" + content + "\n")
            else:
                f.write(content + "\n")
        return {"status": "success", "message": f"Successfully wrote to {note_filename}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
