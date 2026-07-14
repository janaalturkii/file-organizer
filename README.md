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
Open your terminal and run:
git clone https://github.com/janaalturkii/file-organizer.git

Then navigate into the project folder:
cd file-organizer

Everything from this point onwards happens inside this folder.

### Step 2 — Create a virtual environment

A virtual environment is an isolated Python installation just for this
project. It keeps the project's dependencies separate from anything
else on your machine, so installing or upgrading a package here won't
affect other Python projects you have.

Run this to create it:
python -m venv venv

A folder called `venv/` will appear inside your project. You never
need to edit anything inside it directly.

### Step 3 — Activate the virtual environment

Before installing anything or running any code, you must activate the
virtual environment. This tells your terminal to use the project's
isolated Python instead of the system Python.

On Windows:
.\venv\Scripts\activate

On Mac or Linux:
source venv/bin/activate

You will know it worked because your terminal prompt will change to
show `(venv)` at the beginning of the line, like this:
(venv) C:\Projects\file-organizer>

You need to do this every time you open a new terminal window. If you
forget, commands like `pytest` and `pip` may not work correctly.

### Step 4 — Install dependencies

The project uses one external library: `pytest`, for running automated
tests. Install it by running:
pip install -r requirements.txt

This reads the `requirements.txt` file and installs everything listed
in it. You only need to do this once (or after pulling new changes that
add new dependencies).

To confirm pytest installed correctly, run:
pytest --version

You should see a version number printed, like `pytest 8.3.5`.

## Usage

### Basic usage

Run the tool by passing the path to the folder you want to organize:
python -m file_organizer <folder>

Replace `<folder>` with the actual path to your folder. For example:
python -m file_organizer C:\Users\you\Downloads

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
python -m file_organizer C:\Users\you\Downloads

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
images/
photo.jpg
screenshot.png
documents/
resume.pdf
budget.xlsx
notes.txt
videos/
clip.mp4
audio/
music.mp3
archives/
backup.zip
other/
something.xyz

### Preview without moving files

If you want to see what the tool would do without actually moving
anything, use the `--dry-run` flag:
python -m file_organizer <folder> --dry-run

This prints a preview of what would happen and then stops. Nothing
is moved. This is useful if you want to check the tool will behave
as expected before running it on a folder full of real, important files.

### Error handling

If you pass a path that doesn't exist:
python -m file_organizer C:\Users\you\fake-folder
Error: 'C:\Users\you\fake-folder' does not exist.

If you pass a file path instead of a folder:
python -m file_organizer C:\Users\you\photo.jpg
Error: 'C:\Users\you\photo.jpg' is not a folder.

In both cases the tool stops cleanly with a readable message instead
of showing a Python error traceback.

## Supported file types

The following table shows which extensions map to which folder.
Extensions are matched case-insensitively, so `.JPG` and `.jpg`
both go to `images/`.

| Folder      | Extensions                                        |
|-------------|---------------------------------------------------|
| images      | .jpg, .jpeg, .png, .gif, .svg, .webp              |
| documents   | .pdf, .docx, .txt, .xlsx, .csv                    |
| videos      | .mp4, .mov, .avi, .mkv                            |
| audio       | .mp3, .wav, .flac                                 |
| archives    | .zip, .tar, .gz                                   |
| other       | anything not in the list above                    |

To add support for a new file type, open `file_organizer/organizer.py`
and add the extension to the relevant list in `EXTENSION_MAP`, or add
a new category entirely.

## Project structure
file-organizer/
file_organizer/
init.py        # makes this a Python package
main.py        # entry point for python -m file_organizer
organizer.py       # core logic: scanning and moving files
cli.py             # command-line interface using argparse
tests/
init.py
test_main.py       # automated test suite (11+ tests)
.gitignore
README.md
requirements.txt

## Running tests

Run the full test suite with:
pytest -v

All tests should pass. The `-v` flag shows each test by name so you
can see exactly what was checked. The tests cover happy paths (normal
expected usage), average cases (multiple file types at once), and
edge cases (empty folders, files with no extension, invalid paths).

## Interactive mode

Prompt for each file before moving it:

```
python -m file_organizer ~/Downloads --interactive
```

Combine with `--dry-run` to preview decisions without moving anything:

```
python -m file_organizer ~/Downloads --interactive --dry-run
```

Example prompt:

```
photo.jpg
  Suggested: images/
  (a) Accept suggested
  (b) Choose another category
  (c) Skip this file
  (d) Create new custom category
  Your choice [a/b/c/d]: a
```

## Custom Configuration

You can customize how files are categorized without touching the code, using a config file or CLI flags.

**Option 1: Global config** — place a file at `~/.file_organizer/config.yml`. It will be picked up automatically every run.

**Option 2: Per-run config** — pass a path directly with `--config`:
python -m file_organizer /path/to/folder --config my_config.yml

**Option 3: One-off override** — add a single mapping without a file:
python -m file_organizer /path/to/folder --add-extension .log:logs

### Config file format

See `config.example.yml` for a full example. Each key is a category name, and the value is a list of file extensions that belong to it:

```yaml
receipts:
  - .pdf
  - .xlsx
```

Config sources are merged in this order (later sources override earlier ones for the same extension):
1. Built-in defaults
2. `~/.file_organizer/config.yml` (if present)
3. `--config <path>` (if passed)
4. `--add-extension` (if passed)

## Undo / Transaction Log

Every real run (not `--dry-run`) writes a JSON log to `.file_organizer/logs/`, named by timestamp (e.g. `20260708_112520.json`). Each log records every file that was moved during that run — its original location and where it ended up.

### Undoing a run

Undo the most recent run:
python -m file_organizer <folder> --undo

Undo a specific run by its timestamp:
python -m file_organizer <folder> --undo 20260708_112520

If a file's original location is now occupied by something else, or the moved file can no longer be found, that file is skipped and reported instead of being overwritten.

## Logging / Verbosity

By default, the tool prints normal informational output (what moved where). Two flags let you control this:

- `--quiet` — only show warnings and errors
- `--verbose` — show detailed debug output
python -m file_organizer <folder> --quiet
python -m file_organizer <folder> --verbose

## Week 2

See [docs/WEEK2.md](docs/WEEK2.md) for a full retrospective of Week 2
(interactive mode, config overrides, undo/transaction log, watch mode,
and CI), including demo commands and a guide to reviewing the code.