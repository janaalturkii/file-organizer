import logging
import shutil
from pathlib import Path

from file_organizer.organizer import get_all_categories, preview_folder
from file_organizer.logs import write_runlog

logger = logging.getLogger(__name__)


def print_preview(preview: dict[str, list[str]], sample_size: int = 3) -> None:
    """Show counts and a few sample files per suggested folder."""
    print("\nPreview — suggested destinations:")
    for category, files in preview.items():
        print(f"  {category}/ ({len(files)} file(s))")
        for name in files[:sample_size]:
            print(f"    - {name}")
        if len(files) > sample_size:
            print(f"    ... and {len(files) - sample_size} more")


def prompt_for_destination(
    file_name: str, suggested: str, available_categories: list[str]
) -> str | None:
    """Ask the user what to do with one file. Returns the final category, or None to skip."""
    print(f"\n{file_name}")
    print(f"  Suggested: {suggested}/")
    print("  (a) Accept suggested")
    print("  (b) Choose another category")
    print("  (c) Skip this file")
    print("  (d) Create new custom category")
    choice = input("  Your choice [a/b/c/d]: ").strip().lower()

    if choice in ("a", ""):
        return suggested
    if choice == "b":
        print("  Available categories:", ", ".join(available_categories))
        chosen = input("  Type category name: ").strip()
        return chosen or suggested
    if choice == "c":
        return None
    if choice == "d":
        new_category = input("  New category name: ").strip()
        return new_category or suggested

    print("  Not recognized — skipping file.")
    return None


def run_interactive_organize(source: Path, dry_run: bool = False) -> dict[str, int]:
    """Preview, then prompt per file, then move (unless dry_run)."""
    preview = preview_folder(source)
    print_preview(preview)
    available_categories = get_all_categories()

    summary: dict[str, int] = {}
    moves: list[dict] = []

    try:
        for category, files in preview.items():
            for file_name in files:
                decision = prompt_for_destination(file_name, category, available_categories)
                if decision is None:
                    print(f"  Skipped {file_name}")
                    continue

                if dry_run:
                    print(f"  [Dry run] Would move {file_name} -> {decision}/")
                    summary[decision] = summary.get(decision, 0) + 1
                    continue

                dest_dir = source / decision
                dest_dir.mkdir(exist_ok=True)
                original_path = source / file_name
                destination_path = dest_dir / file_name

                # Edge case: don't silently overwrite an existing file at the destination
                if destination_path.exists():
                    print(f"  Warning: {destination_path} already exists — skipping {file_name}")
                    logger.warning(
                        f"Skipped {file_name}: destination already exists at {destination_path}"
                    )
                    continue

                try:
                    shutil.move(str(original_path), str(destination_path))
                except PermissionError:
                    print(f"  Error: permission denied moving {file_name} — skipping")
                    logger.error(f"PermissionError moving {file_name} to {destination_path}")
                    continue
                except OSError as e:
                    print(f"  Error moving {file_name}: {e}")
                    logger.error(f"OSError moving {file_name}: {e}")
                    continue

                logger.info(f"Moved {file_name} -> {decision}/")
                moves.append({
                    "original": str(original_path),
                    "destination": str(destination_path),
                })
                summary[decision] = summary.get(decision, 0) + 1
    finally:
        # Log whatever moves succeeded, even if something above crashed partway through
        if not dry_run and moves:
            write_runlog(str(source), moves)

    return summary