from pathlib import Path

from file_organizer.interactive import prompt_for_destination, run_interactive_organize


def test_accept_suggested(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "a")
    result = prompt_for_destination("photo.jpg", "images", ["images", "documents", "other"])
    assert result == "images"


def test_choose_another_category(monkeypatch):
    answers = iter(["b", "documents"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = prompt_for_destination("photo.jpg", "images", ["images", "documents", "other"])
    assert result == "documents"


def test_skip_file(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "c")
    result = prompt_for_destination("mystery.xyz", "other", ["images", "documents", "other"])
    assert result is None


def test_create_custom_category(monkeypatch):
    answers = iter(["d", "screenshots"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = prompt_for_destination("shot.png", "images", ["images", "documents", "other"])
    assert result == "screenshots"


def test_interactive_dry_run_does_not_move_files(tmp_path: Path, monkeypatch):
    (tmp_path / "a.jpg").touch()
    (tmp_path / "b.pdf").touch()
    monkeypatch.setattr("builtins.input", lambda _: "a")

    run_interactive_organize(tmp_path, dry_run=True)

    assert (tmp_path / "a.jpg").exists()
    assert (tmp_path / "b.pdf").exists()
    assert not (tmp_path / "images").exists()


def test_interactive_moves_files_when_not_dry_run(tmp_path: Path, monkeypatch):
    (tmp_path / "a.jpg").touch()
    monkeypatch.setattr("builtins.input", lambda _: "a")

    summary = run_interactive_organize(tmp_path, dry_run=False)

    assert (tmp_path / "images" / "a.jpg").exists()
    assert summary["images"] == 1