#!/usr/bin/env python3
"""
File Organizer Plugin for Kim 9000
Organizes files in target directories by extension into subfolders.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Extension to category mapping
EXTENSION_MAP: Dict[str, str] = {
    # Images
    **dict.fromkeys(['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.heic'], 'Images'),
    # Videos
    **dict.fromkeys(['.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv', '.wmv', '.m4v'], 'Videos'),
    # Audio
    **dict.fromkeys(['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.opus'], 'Audio'),
    # Documents
    **dict.fromkeys(['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt', '.tex'], 'Documents'),
    # Spreadsheets
    **dict.fromkeys(['.xls', '.xlsx', '.csv', '.tsv', '.ods'], 'Spreadsheets'),
    # Presentations
    **dict.fromkeys(['.ppt', '.pptx', '.odp', '.key'], 'Presentations'),
    # Archives
    **dict.fromkeys(['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar', '.xz', '.tgz'], 'Archives'),
    # Code
    **dict.fromkeys(['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.sh', '.bash', '.zsh', '.fish', '.rs', '.go', '.java', '.kt', '.swift', '.cpp', '.c', '.h', '.hpp'], 'Code'),
    # Config
    **dict.fromkeys(['.ini', '.cfg', '.conf', '.config', '.toml', '.env', '.properties'], 'Config'),
    # Executables
    **dict.fromkeys(['.exe', '.msi', '.apk', '.deb', '.rpm', '.dmg', '.pkg', '.appimage', '.bin'], 'Executables'),
    # Fonts
    **dict.fromkeys(['.ttf', '.otf', '.woff', '.woff2', '.eot'], 'Fonts'),
    # Database
    **dict.fromkeys(['.db', '.sqlite', '.sqlite3', '.realm'], 'Databases'),
    # Logs
    **dict.fromkeys(['.log', '.out', '.err'], 'Logs'),
}

DEFAULT_TARGETS = [
    Path("/root/projects/kim"),
    Path("/root/kim-kai-ecosystem-main"),
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    Path("/root/Downloads"),
    Path("/root/Desktop"),
]

def get_category(ext: str) -> str:
    return EXTENSION_MAP.get(ext.lower(), 'Other')

def organize_directory(target: Path, dry_run: bool = False) -> Dict:
    """Organize files in target directory by extension."""
    if not target.exists():
        return {"error": f"Target does not exist: {target}"}
    
    results = {"moved": [], "skipped": [], "errors": [], "created_dirs": []}
    created_dirs = set()
    
    for item in target.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            ext = item.suffix.lower()
            category = get_category(ext)
            dest_dir = target / category
            
            if not dest_dir.exists():
                if not dry_run:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                created_dirs.add(str(dest_dir))
            
            dest_file = dest_dir / item.name
            
            # Handle collisions
            counter = 1
            original_dest = dest_file
            while dest_file.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            try:
                if not dry_run:
                    shutil.move(str(item), str(dest_file))
                results["moved"].append({
                    "from": str(item),
                    "to": str(dest_file),
                    "category": category
                })
            except Exception as e:
                results["errors"].append({"file": str(item), "error": str(e)})
        else:
            results["skipped"].append(str(item))
    
    results["created_dirs"] = list(created_dirs)
    return results

def run_organizer(targets: Optional[List[str]] = None, dry_run: bool = False) -> Dict:
    """Run organizer on specified targets or defaults."""
    target_paths = [Path(t) for t in targets] if targets else DEFAULT_TARGETS
    all_results = {}
    
    for target in target_paths:
        if target.exists():
            all_results[str(target)] = organize_directory(target, dry_run)
        else:
            all_results[str(target)] = {"error": "Directory not found"}
    
    # Log summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "targets": all_results
    }
    
    log_path = Path.home() / ".local" / "share" / "kim" / "file_organizer.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, "a") as f:
        f.write(json.dumps(summary) + "\n")
    
    return summary

# Kai tool registration
try:
    import builtins
    if hasattr(builtins, 'kai_tool'):
        @builtins.kai_tool("organize_files", "Organize files in target directories by extension")
        def organize_files(targets: List[str] = None, dry_run: bool = False) -> Dict:
            return run_organizer(targets, dry_run)
except ImportError:
    pass

if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else None
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        targets = [t for t in targets if t != "--dry-run"] if targets else None
    
    result = run_organizer(targets, dry_run)
    print(json.dumps(result, indent=2))
