# File Organizer

A command-line tool written in Python that automatically scans a folder
and sorts every file inside it into subfolders based on file type —
images go into `images/`, PDFs and documents go into `documents/`,
videos go into `videos/`, audio files go into `audio/`, compressed
archives go into `archives/`, and anything unrecognized goes into
`other/`. It runs entirely from the terminal with a single command
and reports a summary of what it moved when it's done.

## Why this exists

Folders like Downloads and Desktop accumulate files from everywhere —
screenshots, installers, PDFs you meant to read, random videos someone
sent you — and they pile up fast with no structure. Sorting them by
hand means opening the folder, looking at each file one at a time,
manually creating subfolders, and dragging files into the right place.
For a folder with even fifty files, that's slow and easy to get wrong
or give up on halfway through.

The project was also built as a way to practice writing real,
production-style Python: clean project structure, a proper virtual
environment, type hints, logging instead of print statements, and a
full automated test suite — the habits that separate a script someone
writes once and throws away from a tool that's reliable enough to
actually keep using.

## Installation

Follow these steps exactly, in order, to get the project running on
your machine from scratch.

### Step 1 — Clone the repository

This downloads a copy of the project from GitHub onto your computer.

```bash
git clone https://github.com/janaalturkii/file-organizer.git
cd file-organizer
```

Everything from this point onwards happens inside this folder.

### Step 2 — Create a virtual environment

A virtual environment is an isolated Python installation just for this
project. It keeps the project's dependencies separate from anything
else on your machine, so installing or upgrading a package here won't
affect other Python projects you have.

```bash
python -m venv venv
```

A folder called `venv/` will appear inside your project. You never
need to edit anything inside it directly.

### Step 3 — Activate the virtual environment

Before installing anything or running any code, you must activate the
virtual environment. This tells your terminal to use the project's
isolated Python instead of the system Python.

On Windows:
```powershell
.\venv\Scripts\activate
```

On Mac or Linux:
```bash
source venv/bin/activate
```

You will know it worked because your terminal prompt will change to
show `(venv)` at the beginning of the line, like this:

(venv) C:\Projects\file-organizer>


You need to do this every time you open a new terminal window. If you
forget, commands like `pytest` and `pip` may not work correctly.

### Step 4 — Install dependencies

The project uses one external library: `pytest`, for running automated
tests.

```bash
pip install -r requirements.txt
```

This reads the `requirements.txt` file and installs everything listed
in it. You only need to do this once (or after pulling new changes that
add new dependencies).

To confirm pytest installed correctly:

```bash
pytest --version
```

You should see a version number printed, like `pytest 8.3.5`.

## Usage

### Basic usage

Run the tool by passing the path to the folder you want to organize:

```bash
python -m file_organizer <folder>
```

Replace `<folder>` with the actual path to your folder. For example:

```bash
python -m file_organizer C:\Users\you\Downloads
```

### What happens when you run it

The tool will:

1. Check that the folder you gave it actually exists and is a folder
   (not a file). If not, it prints a clear error message and stops.
2. Loop through every file at the top level of that folder.
3. For each file, look at its extension and decide which subfolder it
   belongs in based on the extension map below.
4. Create that subfolder if it doesn't already exist.
5. Move the file into the subfolder.
6. Log a line to the terminal for each file moved.
7. Print a summary at the end showing how many files went where.

Existing subfolders inside the target folder are never touched — only
loose files at the top level are organized.

### Example

Say `C:\Users\you\Downloads` contains these files:

photo.jpg
screenshot.png
resume.pdf
budget.xlsx
notes.txt
clip.mp4
music.mp3
backup.zip
something.xyz


Running:

```bash
python -m file_organizer C:\Users\you\Downloads
```

Prints this to the terminal:

Organizing C:\Users\you\Downloads ...
Moved photo.jpg → images/
Moved screenshot.png → images/
Moved resume.pdf → documents/
Moved budget.xlsx → documents/
Moved notes.txt → documents/
Moved clip.mp4 → videos/
Moved music.mp3 → audio/
Moved backup.zip → archives/
Moved something.xyz → other/
Done! Summary:
images/: 2 file(s)
documents/: 3 file(s)
videos/: 1 file(s)
audio/: 1 file(s)
archives/: 1 file(s)
other/: 1 file(s)


And the folder now looks like this:

Downloads/
├── images/
│ ├── photo.jpg
│ └── screenshot.png
├── documents/
│ ├── resume.pdf
│ ├── budget.xlsx
│ └── notes.txt
├── videos/
│ └── clip.mp4
├── audio/
│ └── music.mp3
├── archives/
│ └── backup.zip
└── other/
└── something.xyz


### Preview without moving files

If you want to see what the tool would do without actually moving
anything, use the `--dry-run` flag:

```bash
python -m file_organizer <folder> --dry-run
```

This prints a preview of what would happen and then stops. Nothing
is moved. This is useful if you want to check the tool will behave
as expected before running it on a folder full of real, important files.

### Error handling

If you pass a path that doesn't exist:

```bash
python -m file_organizer C:\Users\you\fake-folder
```

Error: 'C:\Users\you\fake-folder' does not exist.


If you pass a file path instead of a folder:

```bash
python -m file_organizer C:\Users\you\photo.jpg
```

Error: 'C:\Users\you\photo.jpg' is not a folder.


In both cases the tool stops cleanly with a readable message instead
of showing a Python error traceback.

## Supported file types

The following table shows which extensions map to which folder.
Extensions are matched case-insensitively, so `.JPG` and `.jpg`
both go to `images/`.

| Folder    | Extensions                           |
|-----------|---------------------------------------|
| images    | .jpg, .jpeg, .png, .gif, .svg, .webp  |
| documents | .pdf, .docx, .txt, .xlsx, .csv        |
| videos    | .mp4, .mov, .avi, .mkv                |
| audio     | .mp3, .wav, .flac                     |
| archives  | .zip, .tar, .gz                       |
| other     | anything not in the list above       |

To add support for a new file type, open `file_organizer/organizer.py`
and add the extension to the relevant list in `EXTENSION_MAP`, or add
a new category entirely.

## Project structure

file-organizer/
├── file_organizer/
│ ├── init.py # makes this a Python package
│ ├── main.py # entry point for python -m file_organizer
│ ├── organizer.py # core logic: scanning and moving files
│ ├── interactive.py # interactive mode prompts
│ ├── config.py # config loading and merging
│ ├── logs.py # transaction logging / undo
│ ├── watcher.py # watch mode + debounce
│ └── cli.py # command-line interface using argparse
├── tests/
│ ├── init.py
│ └── test_*.py # automated test suite (34+ tests)
├── .gitignore
├── README.md
└── requirements.txt


## Running tests

Run the full test suite with:

```bash
pytest -v
```

All tests should pass. The `-v` flag shows each test by name so you
can see exactly what was checked. The tests cover happy paths (normal
expected usage), average cases (multiple file types at once), and
edge cases (empty folders, files with no extension, invalid paths).

## Interactive mode

Prompt for each file before moving it:

```bash
python -m file_organizer ~/Downloads --interactive
```

Combine with `--dry-run` to preview decisions without moving anything:

```bash
python -m file_organizer ~/Downloads --interactive --dry-run
```

Example prompt:

photo.jpg
Suggested: images/
(a) Accept suggested
(b) Choose another category
(c) Skip this file
(d) Create new custom category
Your choice [a/b/c/d]: a


## Custom configuration

You can customize how files are categorized without touching the code,
using a config file or CLI flags.

**Option 1: Global config** — place a file at `~/.file_organizer/config.yml`.
It will be picked up automatically every run.

**Option 2: Per-run config** — pass a path directly with `--config`:

```bash
python -m file_organizer /path/to/folder --config my_config.yml
```

**Option 3: One-off override** — add a single mapping without a file:

```bash
python -m file_organizer /path/to/folder --add-extension .log:logs
```

### Config file format

See `config.example.yml` for a full example. Each key is a category
name, and the value is a list of file extensions that belong to it:

```yaml
receipts:
  - .pdf
  - .xlsx
```

Config sources are merged in this order (later sources override earlier
ones for the same extension):

1. Built-in defaults
2. `~/.file_organizer/config.yml` (if present)
3. `--config <path>` (if passed)
4. `--add-extension` (if passed)

## Undo / transaction log

Every real run (not `--dry-run`) writes a JSON log to
`.file_organizer/logs/`, named by timestamp (e.g. `20260708_112520.json`).
Each log records every file that was moved during that run — its
original location and where it ended up.

### Undoing a run

Undo the most recent run:

```bash
python -m file_organizer <folder> --undo
```

Undo a specific run by its timestamp:

```bash
python -m file_organizer <folder> --undo 20260708_112520
```

If a file's original location is now occupied by something else, or the
moved file can no longer be found, that file is skipped and reported
instead of being overwritten.

## Logging / verbosity

By default, the tool prints normal informational output (what moved
where). Two flags let you control this:

- `--quiet` — only show warnings and errors
- `--verbose` — show detailed debug output

```bash
python -m file_organizer <folder> --quiet
python -m file_organizer <folder> --verbose
```

## Week 2

See [docs/WEEK2.md](docs/WEEK2.md) for a full retrospective of Week 2
(interactive mode, config overrides, undo/transaction log, watch mode,
and CI), including demo commands and a guide to reviewing the code.

## Week 3 — APIs and Claude Fundamentals

This week focused on Anthropic's product ecosystem (Claude 101, Claude Code 101 —
Anthropic Academy) alongside hands-on API work in a separate project
(`daily-summarizer`).

### What was covered
- **Claude 101:** Projects, Artifacts, Cowork, Skills, Connectors (MCP —
  "USB-C for AI"), Enterprise Search, Research Mode, and Claude in a coding
  context (building features, debugging, codebase navigation).
- **Claude Code 101:** installation across terminal/web/IDE, the
  **Explore → Plan → Code → Commit** workflow, and the purpose of a
  `CLAUDE.md` file — giving Claude Code persistent project memory instead
  of re-discovering the codebase every session.

### Applied to this project
- Identified that `file-organizer` had no `CLAUDE.md` yet — flagged as the
  direct next step so Claude Code has standing context on project structure,
  conventions, and known issues (e.g. the PowerShell UTF-16LE encoding gap).
- The Explore → Plan → Code → Commit workflow was adopted going forward for
  all optimization work (see Week 4 below) rather than editing code directly
  without a plan.

## Week 4 — Optimization Pass

Following `OPTIMIZATION_PLAN.md`, this week hardened the existing codebase
against real-world failure, in this order: critical bug fix → edge cases →
exceptions → documentation.

### Critical fix
- `interactive.py` previously used only stdlib `logging` and never called
  into `logs.py`'s transaction logger — meaning `--undo` could not reverse
  interactive-mode runs. Fixed and verified end-to-end (interactive mode →
  undo → files correctly restored).

### Edge cases fixed
- **`interactive.py`** — prevent silent overwrite when a destination
  filename already exists; catch `PermissionError`/`OSError` during file
  moves instead of crashing; wrap the organize loop in `try/finally` so
  partial progress is still logged if a later move fails.
- **`logs.py`** — handle write failures in `write_runlog` with temp-file
  cleanup; handle corrupted or missing-key log files in `undo_run` with
  clear errors instead of raw tracebacks.
- **`config.py`** — handle non-UTF-8/unreadable config files; validate
  extension-map structure (reject non-list/non-string entries per category
  instead of crashing downstream); warn when an explicit `--config` path
  doesn't exist.
- **`watcher.py`** — fixed a debounce self-trigger loop where the organizer
  moving files out of the watched folder was itself re-triggering the
  debounce timer indefinitely.

### Exception audit
- Full-codebase scan for bare `except:`/`except Exception:` found one hit,
  in `watcher.py`. Kept intentionally broad with an inline comment
  explaining why: it runs on a background `Timer` thread, where an
  uncaught exception would silently kill watch mode rather than crash
  visibly.

### Test stability
- Widened timing margins in `test_watcher.py` for three tests sharing a
  thin `0.05s` debounce / `0.1s` wait ratio, after one flaked under
  full-suite thread load. Confirmed via isolated re-runs that the
  underlying logic was correct — this was a test-timing issue, not a
  code bug.

### Documentation
- Reformatted this README for consistent code-block fencing throughout
  (commands, terminal output, and the project structure tree were
  previously unfenced plain text in several sections).

### Testing performed
- Full pytest suite: 34/34 passing, confirmed stable across multiple runs.
- Manual regression pass: `--help`, plain organize, `--config` (valid + 3
  malformed variants: bad encoding, wrong-shape YAML, missing explicit
  path), `--interactive` (accept/choose/skip), `--undo`, `--watch`
  (confirmed single pass per batch, no self-trigger loop), and
  repeated-run duplicate-guard behavior — all confirmed working and
  backward compatible.