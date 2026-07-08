import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Where all run logs get saved. Relative to wherever the tool is run from.
LOG_DIR = Path(".file_organizer") / "logs"


def write_runlog(source_folder: str, moves: list[dict]) -> Path:
    """Write an atomic JSON log of a completed run. Returns the log path."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"{timestamp}.json"
    tmp_path = log_path.with_suffix(".json.tmp")

    data = {
        "timestamp": timestamp,
        "source_folder": source_folder,
        "moves": moves,
    }

    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)

    os.replace(tmp_path, log_path)
    logger.debug(f"Run log written to {log_path}")
    return log_path


def get_latest_log() -> Path | None:
    """Return the path to the most recent run log, or None if there are no logs."""
    logs = sorted(LOG_DIR.glob("*.json"))
    return logs[-1] if logs else None


def undo_run(timestamp: str | None) -> dict:
    """Restore files from a run log. timestamp=None means undo the latest run."""
    if timestamp:
        log_path = LOG_DIR / f"{timestamp}.json"
    else:
        log_path = get_latest_log()

    if not log_path or not log_path.exists():
        raise FileNotFoundError("No matching run log found.")

    with open(log_path) as f:
        data = json.load(f)

    restored: list[str] = []
    skipped: list[str] = []

    for move in data["moves"]:
        original = move["original"]
        destination = move["destination"]

        if Path(original).exists():
            skipped.append(original)
            logger.warning(f"Skipped (conflict): {original} already exists")
            continue

        if Path(destination).exists():
            shutil.move(destination, original)
            restored.append(original)
            logger.info(f"Restored {destination} -> {original}")
        else:
            skipped.append(original)
            logger.warning(f"Skipped (missing): {destination} not found")

    return {"restored": restored, "skipped": skipped}