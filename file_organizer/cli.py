import argparse
from pathlib import Path

from file_organizer.organizer import (
    organize_folder,
    preview_folder,
    EXTENSION_MAP,
    set_extension_map,
)
from file_organizer.interactive import run_interactive_organize, print_preview
from file_organizer.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize files by type.")
    parser.add_argument("folder", type=Path, help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't move files")
    parser.add_argument("--interactive", action="store_true", help="Prompt per file before moving")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML config file with custom extension mappings",
    )
    parser.add_argument(
        "--add-extension",
        action="append",
        metavar="EXT:CATEGORY",
        help="One-off mapping, e.g. --add-extension .log:logs. Can be used multiple times.",
    )
    args = parser.parse_args()

    if not args.folder.exists():
        print(f"Error: '{args.folder}' does not exist.")
        return
    if not args.folder.is_dir():
        print(f"Error: '{args.folder}' is not a folder.")
        return

    # Load and apply any config/overrides BEFORE we do anything with the
    # folder. This has to happen first so that organize_folder/preview_folder
    # use the merged map rather than the hardcoded defaults.
    merged_map = load_config(
        default_map=EXTENSION_MAP,
        config_path=args.config,
        overrides=args.add_extension,
    )
    set_extension_map(merged_map)

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