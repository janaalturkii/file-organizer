# Demo Script

Run these against a scratch folder (`demo_folder`) with a mix of file
types (`.pdf`, `.jpg`, `.mp3`, `.log`, etc.) so each feature has
something to act on.

## 1. Basic organize
```bash
python -m file_organizer ./demo_folder
```
Moves files into subfolders by type.

## 2. Dry run
```bash
python -m file_organizer ./demo_folder --dry-run
```
Shows what *would* move, without moving anything.

## 3. Interactive mode
```bash
python -m file_organizer ./demo_folder --interactive
```
Prompts for confirmation before each individual move.

## 4. Custom config
```bash
python -m file_organizer ./demo_folder --config ~/.file_organizer/config.yml
```
Uses a YAML file to override or extend the default extension → folder
mapping. Also works ad hoc with `--add-extension .log:logs`.

## 5. Undo
```bash
python -m file_organizer --undo
```
Restores files from the most recent run's transaction log. Add a
timestamp (`--undo 20260708_112520`) to restore a specific earlier run
instead of the latest one.

## 6. Watch mode
```bash
python -m file_organizer ./demo_folder --watch
```
Leave this running, then in a **separate terminal window**, drop a few
new files into `demo_folder`:
```bash
echo test > demo_folder/notes.txt
```
Watch mode should organize it automatically after ~2 seconds (the
debounce window). Press `Ctrl+C` to stop watching.

## 7. Verbosity flags
```bash
python -m file_organizer ./demo_folder --verbose
python -m file_organizer ./demo_folder --quiet
```
Compare the amount of logging output between the two.