import logging
import shutil
from pathlib import Path

from file_organizer.logs import write_runlog

# This module only creates a logger and uses it — it does NOT configure
# logging (no basicConfig() here). Configuration (setting the level,
# format, etc.) is the responsibility of the entry point (cli.py's
# setup_logging()). Keeping config in one place means whoever runs
# the program controls verbosity (e.g. --quiet/--verbose), and this
# module behaves consistently whether it's run from the CLI or
# imported and used elsewhere (like in tests).
logger = logging.getLogger(__name__)

# Maps each destination folder name to the list of file extensions
# that belong there. Extensions are stored in lowercase — we use
# .lower() when comparing so the matching is case-insensitive.
# To add a new file type, just add its extension to the right list.
EXTENSION_MAP: dict[str, list[str]] = {
    "images":    [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
    "documents": [".pdf", ".docx", ".txt", ".xlsx", ".csv"],
    "videos":    [".mp4", ".mov", ".avi", ".mkv"],
    "audio":     [".mp3", ".wav", ".flac"],
    "archives":  [".zip", ".tar", ".gz"],
}

# The map actually used at runtime. Starts as a copy of the default; can be
# replaced by set_extension_map() once config.py has merged in user settings.
# We copy EXTENSION_MAP rather than pointing at it directly so that mutating
# the active map at runtime never mutates the original defaults.
_active_extension_map: dict[str, list[str]] = dict(EXTENSION_MAP)


def get_extension_map() -> dict[str, list[str]]:
    """Return the currently active extension map (defaults + any config merged in)."""
    return _active_extension_map


def set_extension_map(new_map: dict[str, list[str]]) -> None:
    """Replace the active extension map (called by the CLI after loading config)."""
    global _active_extension_map
    _active_extension_map = new_map


def get_destination(extension: str) -> str:
    """Return the folder name for a given file extension.

    Loops through the active extension map and returns the folder name
    whose list contains the given extension. The comparison is
    case-insensitive so .JPG and .jpg both return 'images'.

    If no match is found, returns 'other' so unknown file types
    are always handled gracefully instead of raising an error.
    """
    extension_map = get_extension_map()
    for folder, extensions in extension_map.items():
        if extension.lower() in extensions:
            return folder
    return "other"


def organize_folder(source: Path) -> dict[str, int]:
    """Move all files in source into subfolders sorted by type.

    Scans every item at the top level of source. For each file,
    determines the correct destination subfolder using
    get_destination(), creates that subfolder if needed, and
    moves the file into it.

    Subfolders that already exist inside source are left alone —
    only loose files at the top level are moved.

    After moving files, writes a transaction log recording every
    original -> destination move, so the run can later be undone
    with --undo.

    Args:
        source: Path to the folder to organize.

    Returns:
        A summary dictionary mapping folder names to the number
        of files moved there, e.g. {"images": 3, "documents": 2}.

    Raises:
        ValueError: If source is not an existing directory.
    """
    if not source.is_dir():
        raise ValueError(f"Not a directory: {source}")

    summary: dict[str, int] = {}
    moves: list[dict[str, str]] = []

    for file_path in source.iterdir():
        # Skip subfolders — we only organize files, not nested folders.
        if not file_path.is_file():
            continue

        dest_name = get_destination(file_path.suffix)
        dest_dir = source / dest_name

        dest_dir.mkdir(exist_ok=True)

        destination_file = dest_dir / file_path.name
        if destination_file.exists():
            logger.info(f"  Skipped {file_path.name} (already exists in {dest_name}/)")
            continue

        # Record the move BEFORE we do it, using the exact paths involved.
        # We do this here (not at the end) so that even if something goes
        # wrong partway through the loop, "moves" always reflects exactly
        # what actually happened so far.
        original_path = str(file_path)
        destination_path = str(destination_file)

        shutil.move(original_path, destination_path)
        logger.info(f"  Moved {file_path.name} → {dest_name}/")

        moves.append({"original": original_path, "destination": destination_path})
        summary[dest_name] = summary.get(dest_name, 0) + 1

    # Only write a log if files actually moved. An empty run (nothing to
    # organize) doesn't need a log entry, and there'd be nothing to undo.
    if moves:
        log_path = write_runlog(str(source), moves)
        logger.debug(f"Run log written to {log_path}")

    return summary


def get_all_categories() -> list[str]:
    """Return every known category name, for use in interactive prompts."""
    return sorted(get_extension_map().keys()) + ["other"]


def preview_folder(source: Path) -> dict[str, list[str]]:
    """Group files by suggested destination WITHOUT moving anything."""
    if not source.is_dir():
        raise ValueError(f"Not a directory: {source}")
    preview: dict[str, list[str]] = {}
    for file_path in source.iterdir():
        if not file_path.is_file():
            continue
        dest_name = get_destination(file_path.suffix)
        preview.setdefault(dest_name, []).append(file_path.name)
    return preview