import argparse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

from file_organizer.organizer import (
    organize_folder,
    preview_folder,
    EXTENSION_MAP,
    set_extension_map,
)
from file_organizer.interactive import run_interactive_organize, print_preview
from file_organizer.config import load_config
from file_organizer.logs import undo_run


def setup_logging(quiet: bool, verbose: bool) -> None:
    """Configure logging level based on CLI flags."""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        force=True,
    )


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
    parser.add_argument(
        "--undo",
        nargs="?",
        const="latest",
        default=None,
        help="Undo the last run, or a specific run by timestamp (e.g. --undo 20260708_112520)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch the folder for new files and organize them automatically.",
    )
    parser.add_argument(
        "--debounce",
        type=float,
        default=2.0,
        help="Seconds to wait after the last file event before organizing (default: 2.0).",
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("--quiet", action="store_true", help="Only show warnings and errors")
    verbosity.add_argument("--verbose", action="store_true", help="Show debug output")

    args = parser.parse_args()

    setup_logging(args.quiet, args.verbose)

    if args.undo:
        timestamp = None if args.undo == "latest" else args.undo
        try:
            result = undo_run(timestamp)
        except FileNotFoundError as e:
            logger.error(str(e))
            return

        logger.info(f"Restored {len(result['restored'])} file(s), skipped {len(result['skipped'])}")
        for path in result["restored"]:
            logger.info(f"  Restored: {path}")
        for path in result["skipped"]:
            logger.warning(f"  Skipped: {path}")
        return

    if not args.folder.exists():
        logger.error(f"Error: '{args.folder}' does not exist.")
        return
    if not args.folder.is_dir():
        logger.error(f"Error: '{args.folder}' is not a folder.")
        return

    merged_map = load_config(
        default_map=EXTENSION_MAP,
        config_path=args.config,
        overrides=args.add_extension,
    )
    set_extension_map(merged_map)

    if args.watch:
        from file_organizer.watcher import watch_folder

        def organize_callback():
            if args.interactive:
                summary = run_interactive_organize(args.folder, dry_run=args.dry_run)
                logger.info("\n[Dry run complete]" if args.dry_run else "\nDone!")
                for folder, count in summary.items():
                    logger.info(f"  {folder}/: {count} file(s)")
            elif args.dry_run:
                preview = preview_folder(args.folder)
                print_preview(preview)
                logger.info("\n[Dry run — no files moved]")
            else:
                summary = organize_folder(args.folder)
                logger.info("Done!")
                for folder, count in summary.items():
                    logger.info(f"  {folder}/: {count} file(s)")

        watch_folder(args.folder, organize_callback, debounce_seconds=args.debounce)
        return

    if args.interactive:
        summary = run_interactive_organize(args.folder, dry_run=args.dry_run)
        logger.info("\n[Dry run complete]" if args.dry_run else "\nDone!")
        for folder, count in summary.items():
            logger.info(f"  {folder}/: {count} file(s)")
        return

    if args.dry_run:
        preview = preview_folder(args.folder)
        print_preview(preview)
        logger.info("\n[Dry run — no files moved]")
        return

    logger.info(f"Organizing {args.folder} ...")
    summary = organize_folder(args.folder)
    logger.info("Done!")
    for folder, count in summary.items():
        logger.info(f"  {folder}/: {count} file(s)")


if __name__ == "__main__":
    main()