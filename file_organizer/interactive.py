import logging
import shutil
from pathlib import Path

from file_organizer.organizer import get_all_categories, preview_folder

logger = logging.getLogger(__name__)


class ExitInteractiveMode(Exception):
    """Raised when the user chooses to exit interactive mode early."""
    pass


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
    print("  (e) Exit interactive mode")
    choice = input("  Your choice [a/b/c/d/e]: ").strip().lower()

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
    if choice == "e":
        raise ExitInteractiveMode()

    print("  Not recognized — skipping file.")
    return None


def run_interactive_organize(source: Path, dry_run: bool = False) -> dict[str, int]:
    """Preview, then prompt per file, then move (unless dry_run)."""
    preview = preview_folder(source)
    print_preview(preview)
    available_categories = get_all_categories()

    summary: dict[str, int] = {}
    for category, files in preview.items():
        for file_name in files:
            decision = prompt_for_destination(file_name, category, available_categories)
            if decision is None:
                print(f"  Skipped {file_name}")
                continue

            if dry_run:
                print(f"  [Dry run] Would move {file_name} -> {decision}/")
            else:
                dest_dir = source / decision
                dest_dir.mkdir(exist_ok=True)
                shutil.move(str(source / file_name), dest_dir / file_name)
                logger.info(f"Moved {file_name} -> {decision}/")
<<<<<<< Updated upstream
=======
                moves.append({
                    "original": str(original_path),
                    "destination": str(destination_path),
                })
                summary[decision] = summary.get(decision, 0) + 1
    except ExitInteractiveMode:
        print("\nExiting interactive mode early. Saving progress so far...")
    finally:
        # Log whatever moves succeeded, even if something above crashed partway through
        if not dry_run and moves:
            write_runlog(str(source), moves)
>>>>>>> Stashed changes

            summary[decision] = summary.get(decision, 0) + 1
    return summary 