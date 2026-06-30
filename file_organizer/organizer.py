
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

EXTENSION_MAP: dict[str, list[str]] = {
    "images":    [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
    "documents": [".pdf", ".docx", ".txt", ".xlsx", ".csv"],
    "videos":    [".mp4", ".mov", ".avi", ".mkv"],
    "audio":     [".mp3", ".wav", ".flac"],
    "archives":  [".zip", ".tar", ".gz"],
}

def get_destination(extension: str) -> str:
    """Return the folder name for a given file extension."""
    for folder, extensions in EXTENSION_MAP.items():
        if extension.lower() in extensions:
            return folder
    return "other"

def organize_folder(source: Path) -> dict[str, int]:
    """Move files in source into subfolders by type."""
    if not source.is_dir():
        raise ValueError(f"Not a directory: {source}")
    summary: dict[str, int] = {}
    for file_path in source.iterdir():
        if not file_path.is_file():
            continue
        dest_name = get_destination(file_path.suffix)
        dest_dir = source / dest_name
        dest_dir.mkdir(exist_ok=True)
        shutil.move(str(file_path), dest_dir / file_path.name)
        logger.info(f"  Moved {file_path.name} → {dest_name}/")
        summary[dest_name] = summary.get(dest_name, 0) + 1
    return summary
