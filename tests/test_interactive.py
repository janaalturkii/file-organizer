from pathlib import Path

import pytest

from file_organizer.interactive import (
    ExitInteractiveMode,
    prompt_for_destination,
    run_interactive_organize,
)


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


# --- NEW: unit test for the exit option, grouped with the other per-option tests ---
def test_exit_option_raises(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "e")
    with pytest.raises(ExitInteractiveMode):
        prompt_for_destination("anything.txt", "other", ["images", "documents", "other"])


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


# --- NEW: integration-level tests for exiting mid-session, grouped with the other run_interactive_organize tests ---
def test_exit_option_stops_interactive_mode(tmp_path: Path, monkeypatch):
    """Choosing 'e' should exit cleanly without raising, and skip remaining files."""
    (tmp_path / "a.jpg").touch()
    (tmp_path / "b.png").touch()

    responses = iter(["a", "e"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    summary = run_interactive_organize(tmp_path)

    assert isinstance(summary, dict)
    assert sum(summary.values()) == 1  # only the accepted file counted
    assert (tmp_path / "images" / "a.jpg").exists()


def test_exit_immediately_returns_empty_summary(tmp_path: Path, monkeypatch):
    """Exiting on the very first file should return an empty summary, no crash."""
    (tmp_path / "a.jpg").touch()
    monkeypatch.setattr("builtins.input", lambda _: "e")

    summary = run_interactive_organize(tmp_path)

    assert summary == {}