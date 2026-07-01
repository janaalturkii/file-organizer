
import logging
import shutil
from pathlib import Path

# Set up logging so the tool prints informative messages to the
# terminal as it runs. Using logging instead of print() means we
# can control verbosity level in the future (e.g. silence output
# in tests) without changing any function code.
logging.basicConfig(level=logging.INFO, format="%(message)s")
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


def get_destination(extension: str) -> str:
    """Return the folder name for a given file extension.

    Loops through EXTENSION_MAP and returns the folder name whose
    list contains the given extension. The comparison is
    case-insensitive so .JPG and .jpg both return 'images'.

    If no match is found, returns 'other' so unknown file types
    are always handled gracefully instead of raising an error.
    """
    for folder, extensions in EXTENSION_MAP.items():
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

    Args:
        source: Path to the folder to organize.

    Returns:
        A summary dictionary mapping folder names to the number
        of files moved there, e.g. {"images": 3, "documents": 2}.

    Raises:
        ValueError: If source is not an existing directory.
    """
    # Fail early with a clear message if the path isn't a real folder.
    # This is better than letting shutil or iterdir raise a confusing
    # low-level error later.
    if not source.is_dir():
        raise ValueError(f"Not a directory: {source}")

    summary: dict[str, int] = {}

    for file_path in source.iterdir():
        # Skip subfolders — we only organize files, not nested folders.
        # This prevents the tool from accidentally moving a subfolder
        # that the user created intentionally.
        if not file_path.is_file():
            continue

        # Get the destination folder name based on the file extension.
        dest_name = get_destination(file_path.suffix)
        dest_dir = source / dest_name

        # Create the destination subfolder if it doesn't exist yet.
        # exist_ok=True means this won't raise an error if it's
        # already there from a previous run.
        dest_dir.mkdir(exist_ok=True)

        # Skip files that already exist in the destination to avoid
        # accidentally overwriting a file with the same name.
        destination_file = dest_dir / file_path.name
        if destination_file.exists():
            logger.info(f"  Skipped {file_path.name} (already exists in {dest_name}/)")
            continue

        # Move the file and log what happened.
        shutil.move(str(file_path), destination_file)
        logger.info(f"  Moved {file_path.name} → {dest_name}/")

        # Count how many files went to each folder for the summary.
        summary[dest_name] = summary.get(dest_name, 0) + 1

    return summary 