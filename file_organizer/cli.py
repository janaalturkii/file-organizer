import argparse
from pathlib import Path

from file_organizer.organizer import organize_folder, preview_folder
from file_organizer.interactive import run_interactive_organize, print_preview


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize files by type.")
    parser.add_argument("folder", type=Path, help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't move files")
    parser.add_argument("--interactive", action="store_true", help="Prompt per file before moving")
    args = parser.parse_args()

    if not args.folder.exists():
        print(f"Error: '{args.folder}' does not exist.")
        return
    if not args.folder.is_dir():
        print(f"Error: '{args.folder}' is not a folder.")
        return

    if args.interactive:
        summary = run_interactive_organize(args.folder, dry_run=args.dry_run)
        print("\n[Dry run complete]" if args.dry_run else "\nDone!")
        for folder, count in summary.items():
            print(f"  {folder}/: {count} file(s)")
        return

    if args.dry_run:
        preview = preview_folder(args.folder)
        print_preview(preview)
        print("\n[Dry run — no files moved]")
        return

    print(f"Organizing {args.folder} ...")
    summary = organize_folder(args.folder)
    print("Done!")
    for folder, count in summary.items():
        print(f"  {folder}/: {count} file(s)")