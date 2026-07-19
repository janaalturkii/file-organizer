# Optimization Plan — file-organizer

**Prepared:** Week 3/4 review
**Scope:** Documentation, Readability, Logging, Edge Cases, Exceptions

This plan follows the Explore → Plan → Code → Commit workflow. Each item below is a candidate for its own small branch/PR, in line with the project's existing one-feature-per-branch convention.

---

## 1. Documentation

| Priority | Item | Why |
|---|---|---|
| High | Add module-level docstrings to `organizer.py`, `interactive.py`, `config.py`, `logs.py` | Each file should state its purpose in 2-3 lines at the top so a new reader (or trainer) doesn't have to reverse-engineer intent from code |
| High | Add function-level docstrings (params, return type, raised exceptions) to every public function, especially `get_destination()`, `organize_folder()`, the config merge function, and the transaction logger | Currently these are the "load-bearing" functions of the project — undocumented behavior here is the highest-risk gap |
| Medium | Document the 4-layer config precedence directly in `config.py`, not just in README | Precedence rules (defaults → global config → `--config` → `--add-extension`) are easy to get backwards; a code comment prevents future regressions |
| Medium | Add a `docs/ARCHITECTURE.md` describing how the 4 modules interact (e.g. a simple flow: CLI → organizer → config/logs) | Useful now that the project has grown past a single-file script |
| Low | Add a CHANGELOG.md summarizing what shipped each week | Nice-to-have for trainer review and for your own portfolio narrative |

## 2. Readability

| Priority | Item | Why |
|---|---|---|
| High | Extract the repeated "resolve destination folder for extension" logic if it's duplicated between `organizer.py` and `interactive.py` | Interactive mode likely re-implements parts of the core organize logic instead of reusing it — worth checking and consolidating |
| Medium | Standardize naming: confirm `organizer.py` and `interactive.py` use consistent parameter names (e.g. `src_path` vs `source`) | Small inconsistencies compound as the codebase grows |
| Medium | Add type hints anywhere still missing (you started with type hints in Week 1 — check they carried through to Week 2's new files) | Keeps the whole project consistent and catches bugs early |
| Low | Break up any function over ~30-40 lines (watch mode + debounce logic is a likely candidate) | Easier to test and reason about in smaller pieces |

## 3. Logging

| Priority | Item | Why |
|---|---|---|
| **Critical** | Fix the known gap: `interactive.py` uses only stdlib `logging` and never calls into `logs.py`'s transaction logger, so `--undo` cannot reverse interactive-mode runs | This is a real functional bug, not just a style issue — flag it to your trainer as something you identified and are fixing |
| Medium | Confirm `--quiet`/`--verbose` flags apply consistently across all modules (organizer, interactive, watch mode) | Watch mode and interactive mode were added after the verbosity fix — worth double-checking they inherited it correctly |
| Low | Consider log rotation or a max-size cap on the transaction log file if it's meant to grow over many runs | Not urgent, but worth a comment/TODO if out of scope for now |

## 4. Edge Cases

| Priority | Item | Why |
|---|---|---|
| High | Malformed or missing YAML config file — does `config.py` fail gracefully or crash? | A bad `~/.file_organizer/config.yml` shouldn't take down the whole tool |
| High | Duplicate filenames during organize — confirm this still works correctly now that interactive mode, watch mode, and config overrides all touch file placement | Original Week 1 logic handled this; verify it still holds with the new code paths layered on top |
| Medium | Permission errors (read-only files, locked files on Windows) | Common on Windows especially with OneDrive/Defender interaction already seen in this project |
| Medium | Watch mode + debounce race condition: what happens if a file is modified again mid-debounce, or deleted before the debounce timer fires? | Watch mode is the newest, least-tested feature |
| Low | Empty source folder / no matching extensions | Should exit cleanly with a clear message, not silently do nothing |

## 5. Exceptions

| Priority | Item | Why |
|---|---|---|
| High | Audit for bare `except:` or overly broad `except Exception:` blocks | These hide real bugs; replace with specific exception types where possible |
| Medium | Ensure `logs.py`'s atomic write (`os.replace`) has proper exception handling if the write fails mid-operation | Undo relies on this log being trustworthy — a silent partial write would corrupt undo history |
| Medium | Give CLI-facing errors user-friendly messages (not raw tracebacks) for expected failure cases (bad path, bad config, permission denied) | Improves usability without needing new dependencies |
| Low | Consider a custom exception hierarchy (e.g. `FileOrganizerError` base class) if error handling logic grows further | Not urgent at current project size, but worth flagging as a future improvement |

---

## Suggested Order of Attack
1. **Critical fix first:** wire `interactive.py` into `logs.py` so undo works for interactive mode (Logging #1)
2. **Edge case audit:** malformed config + duplicate filenames + permission errors (Edge Cases, High priority)
3. **Exception audit:** find and fix broad except blocks (Exceptions, High priority)
4. **Documentation pass:** docstrings across all 4 modules (Documentation, High priority)
5. **Readability cleanup:** de-duplicate logic between organizer and interactive (Readability, High priority)
6. Everything else (Medium/Low) as time allows, each as its own small branch/PR

This order fixes the one confirmed functional bug first, then hardens the code against real-world failure before polishing style and docs — which is generally the right sequence to defend to a trainer if asked "why this order."