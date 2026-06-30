from pathlib import Path
import pytest
from file_organizer.organizer import get_destination, organize_folder


def test_jpg_is_image():
    assert get_destination(".jpg") == "images"


def test_pdf_is_document():
    assert get_destination(".pdf") == "documents"


def test_unknown_extension_is_other():
    assert get_destination(".xyz") == "other"


def test_extension_is_case_insensitive():
    assert get_destination(".JPG") == "images"


def test_image_file_is_moved(tmp_path: Path):
    (tmp_path / "photo.jpg").touch()
    organize_folder(tmp_path)
    assert (tmp_path / "images" / "photo.jpg").exists()


def test_multiple_types_organized(tmp_path: Path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "clip.mp4").touch()
    summary = organize_folder(tmp_path)
    assert summary["images"] == 1
    assert summary["documents"] == 1
    assert summary["videos"] == 1


def test_invalid_folder_raises_error():
    with pytest.raises(ValueError):
        organize_folder(Path("/this/does/not/exist"))