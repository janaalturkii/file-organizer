from pathlib import Path
from file_organizer import logs as logs_module
from file_organizer.logs import write_runlog, undo_run


def test_undo_restores_files(tmp_path, monkeypatch):
    """A normal move should be fully reversed by undo_run()."""

    # Point LOG_DIR at a temp folder for this test only.
    fake_log_dir = tmp_path / ".file_organizer" / "logs"
    monkeypatch.setattr(logs_module, "LOG_DIR", fake_log_dir)

    # Simulate a file that the organizer already "moved".
    original = tmp_path / "photo.jpg"
    original.write_text("fake image data")

    dest_folder = tmp_path / "images"
    dest_folder.mkdir()
    destination = dest_folder / "photo.jpg"

    original.rename(destination)  # pretend organize_folder already did this

    # Write a run log describing that move, same as organize_folder() would.
    moves = [{"original": str(original), "destination": str(destination)}]
    log_path = write_runlog(str(tmp_path), moves)
    timestamp = log_path.stem  # filename without ".json"

    # Now undo it.
    result = undo_run(timestamp)

    assert original.exists()
    assert not destination.exists()
    assert str(original) in result["restored"]
    assert result["skipped"] == []


def test_undo_reports_conflict(tmp_path, monkeypatch):
    """If the original path is occupied again, undo should skip, not overwrite."""

    fake_log_dir = tmp_path / ".file_organizer" / "logs"
    monkeypatch.setattr(logs_module, "LOG_DIR", fake_log_dir)

    original = tmp_path / "doc.txt"
    dest_folder = tmp_path / "documents"
    dest_folder.mkdir()
    destination = dest_folder / "doc.txt"
    destination.write_text("moved file")

    # Simulate a conflict: something NEW now sits at the original path.
    original.write_text("a different new file created after the move")

    moves = [{"original": str(original), "destination": str(destination)}]
    log_path = write_runlog(str(tmp_path), moves)
    timestamp = log_path.stem

    result = undo_run(timestamp)

    assert str(original) in result["skipped"]
    assert result["restored"] == []
    # The conflicting file at "original" should be untouched.
    assert original.read_text() == "a different new file created after the move"


def test_undo_with_no_timestamp_uses_latest(tmp_path, monkeypatch):
    """Calling undo_run(None) should restore the most recent run."""

    fake_log_dir = tmp_path / ".file_organizer" / "logs"
    monkeypatch.setattr(logs_module, "LOG_DIR", fake_log_dir)

    original = tmp_path / "notes.txt"
    original.write_text("hello")
    dest_folder = tmp_path / "documents"
    dest_folder.mkdir()
    destination = dest_folder / "notes.txt"
    original.rename(destination)

    moves = [{"original": str(original), "destination": str(destination)}]
    write_runlog(str(tmp_path), moves)  # don't need the returned path this time

    result = undo_run(None)  # None = "undo the latest run"

    assert original.exists()
    assert str(original) in result["restored"]