import pytest
from file_organizer.config import merge_extension_maps, load_config


def test_merge_extension_maps_basic():
    defaults = {"images": [".jpg", ".png"]}
    override = {"images": [".gif"], "docs": [".pdf"]}
    result = merge_extension_maps(defaults, override)

    assert ".jpg" in result["images"]
    assert ".gif" in result["images"]
    assert ".pdf" in result["docs"]


def test_merge_extension_maps_conflict_later_wins():
    defaults = {"images": [".pdf"]}
    override = {"docs": [".pdf"]}
    result = merge_extension_maps(defaults, override)

    # .pdf should end up under "docs" since override came later
    assert ".pdf" in result["docs"]
    assert ".pdf" not in result.get("images", [])


def test_load_config_no_files_returns_defaults(tmp_path, monkeypatch):
    # Point the "home config" path somewhere that doesn't exist
    monkeypatch.setattr(
        "file_organizer.config.DEFAULT_CONFIG_PATH", tmp_path / "nonexistent.yml"
    )
    defaults = {"images": [".jpg"]}
    result = load_config(default_map=defaults)
    assert result == {"images": [".jpg"]}


def test_load_config_with_cli_config_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "file_organizer.config.DEFAULT_CONFIG_PATH", tmp_path / "nonexistent.yml"
    )
    config_file = tmp_path / "custom.yml"
    config_file.write_text("receipts:\n  - .pdf\n  - .xlsx\n")

    defaults = {"images": [".jpg"]}
    result = load_config(default_map=defaults, config_path=str(config_file))

    assert ".pdf" in result["receipts"]
    assert ".xlsx" in result["receipts"]
    assert ".jpg" in result["images"]


def test_load_config_with_overrides():
    defaults = {"images": [".jpg"]}
    result = load_config(default_map=defaults, overrides=[".log:logs"])
    assert ".log" in result["logs"]