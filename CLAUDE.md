# CLAUDE.md

This file gives Claude Code persistent context on the `file-organizer` project so it doesn't have to re-explore from scratch each session.

## Project Overview
A Python CLI tool that organizes files into folders based on file extension. Built incrementally over a structured internship curriculum (Week 1: core organizer, Week 2: interactive mode, config, undo/logging, verbosity, watch mode).

- **Repo:** github.com/janaalturkii/file-organizer
- **Language:** Python 3.11 and 3.13 (both tested in CI)
- **Platform:** Developed on Windows, VS Code, PowerShell terminal

## Project Structure
- `organizer.py` — core logic: `get_destination()`, `organize_folder()`
- `interactive.py` — interactive per-file prompt mode
- `config.py` — YAML config loading with 4-layer merge precedence:
  defaults → `~/.file_organizer/config.yml` → `--config` path → `--add-extension`
- `logs.py` — transaction logging for undo support; writes JSON atomically via `os.replace`
- `__main__.py` — CLI entry point (argparse)
- `tests/` — pytest test suite
- `docs/` — WEEK2.md, WEEK3.md, etc.
- `scripts/demo.md` — demo walkthrough script
- `.github/workflows/` — CI running pytest on Python 3.11 & 3.13, Ubuntu

## Known Issues / Gaps
1. **Undo does not work for interactive mode.** `interactive.py` only uses Python's standard `logging` module and never calls into `logs.py`'s transaction logger. This means `--undo` cannot reverse any run that used `--interactive`. This is a known gap to fix.
2. **PowerShell UTF-16LE encoding issue.** Files created via PowerShell redirects (e.g. `> file.txt`) get saved as UTF-16LE, which causes `SyntaxError: source code string cannot contain null bytes` when pytest tries to import them. This has broken `.gitignore` and `tests/__init__.py` in the past.
   - **Workaround:** always create/edit files directly in VS Code, never via PowerShell redirects.
   - Windows Defender/OneDrive interaction is a suspected contributing factor. Project was moved out of OneDrive (`C:\Projects\file-organizer`) to mitigate this.

## Conventions
- One feature per daily branch, one PR per day merging into `main`.
- Recent branch naming fix: use descriptive names like `feature/transaction-log` (avoid day-based names like `feature/day5-automation-and-docs`).
- Follow **Explore → Plan → Code → Commit** — don't jump straight to writing code without first exploring the relevant files and proposing a plan.

## Testing
- Test runner: `pytest`
- If pytest fails locally with a null-byte/encoding error, it's very likely the PowerShell UTF-16LE issue above — check file encoding before assuming a logic bug.

## Commands
- Run tests: `pytest`
- Run CLI: `python -m file_organizer [args]`
- Undo last run: `python -m file_organizer --undo`
- Watch mode: `python -m file_organizer --watch --debounce <seconds>`