import argparse
from pathlib import Path
from file_organizer.organizer import organize_folder


def main() -> None:
    """Run the file organizer from the command line."""
    parser = argparse.ArgumentParser(
        description="Organize files in a folder by type."
    )
    parser.add_argument("folder", type=Path, help="Folder to organize")
    args = parser.parse_args()

    if not args.folder.exists():
        print(f"Error: '{args.folder}' does not exist.")
        return

    if not args.folder.is_dir():
        print(f"Error: '{args.folder}' is not a folder.")
        return

    print(f"Organizing {args.folder} ...")
    summary = organize_folder(args.folder)

    print("Done! Summary:")
    for folder, count in summary.items():
        print(f"  {folder}/: {count} file(s)")