# Week 2 Retrospective

## What was added

- **Interactive mode** (`feature/interactive-mode`): preview + per-file
  confirmation before moving files, via `--interactive`.
- **Configurable extension map** (`feature/config-overrides`): a
  four-layer YAML config merge (defaults → user config file → one-off
  `--add-extension` flags), via `--config` and `--add-extension`.
- **Undo / transaction log** (`feature/undo-transaction-log`): every
  real run writes a JSON log of what moved where; `--undo` restores
  from it, skipping (and reporting) conflicts instead of overwriting.
  Also added `--quiet` / `--verbose` logging levels.
- **Watch mode** (Day 5): `--watch` monitors a folder and
  auto-organizes new files after a debounce period, reusing the exact
  same interactive/dry-run logic as a one-shot run.
- **CI**: GitHub Actions runs `pytest` on every push and PR, across
  Python 3.11 and 3.13 (`.github/workflows/python.yml`).

## Demo commands

```bash
# Dry run — preview only, no files moved
python -m file_organizer ./sample_folder --dry-run

# Interactive mode — confirm each move
python -m file_organizer ./sample_folder --interactive

# Custom config
python -m file_organizer ./sample_folder --config ~/.file_organizer/config.yml

# Undo the last run
python -m file_organizer --undo

# Undo a specific run
python -m file_organizer --undo 20260708_112520

# Watch mode
python -m file_organizer ./sample_folder --watch --debounce 2
```

## How to review the code

- `file_organizer/organizer.py` — core organize/preview logic
- `file_organizer/interactive.py` — interactive mode prompts
- `file_organizer/config.py` — YAML config loading and merging
- `file_organizer/logs.py` — transaction log writing + undo logic
- `file_organizer/watcher.py` — watch mode (debounced file-system events)
- `file_organizer/cli.py` (or `__main__.py`) — argument parsing, wires
  everything together
- `tests/` — mirrors the module structure above, one test file per
  module

## Notable bug fixed this week

A top-level `logging.basicConfig()` call in `organizer.py` ran on
import, before `cli.py`'s own `setup_logging()` could run. Since
`basicConfig()` is a no-op once the root logger is already configured,
this silently broke `--quiet`/`--verbose` — the flags parsed
correctly but had zero effect. Fixed by removing the top-level call
and adding `force=True` to `setup_logging()`, since a single process
may now call it more than once (e.g. across tests).

## Known environment issue

Windows + OneDrive + Defender occasionally corrupts newly created
files with null bytes or UTF-16LE encoding, which breaks `pytest`
locally. See `CONTRIBUTING.md` for the full writeup and workaround.
This was also the root cause of an early CI failure this week — traced
down to `tests/__init__.py` having been created via a PowerShell `>`
redirect rather than in VS Code.