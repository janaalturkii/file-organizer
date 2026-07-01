from pathlib import Path
import pytest
from file_organizer.organizer import get_destination, organize_folder


# ── Happy path tests ─────────────────────────────────────────────
# These test the most common, expected usage of the functions.
# If these fail, something is fundamentally broken.

def test_jpg_is_image():
    """A .jpg file extension should map to the 'images' folder.
    This is the most basic happy path — a common file type that
    every user would expect to be sorted correctly."""
    assert get_destination(".jpg") == "images"


def test_pdf_is_document():
    """A .pdf file extension should map to the 'documents' folder.
    PDFs are one of the most common document types users will have
    in a downloads folder."""
    assert get_destination(".pdf") == "documents"


def test_image_file_is_moved(tmp_path: Path):
    """A .jpg file placed in a folder should be physically moved
    into an 'images/' subfolder when organize_folder() runs.
    This tests the full end-to-end happy path: file exists,
    function runs, file is in the right place afterwards."""
    (tmp_path / "photo.jpg").touch()
    organize_folder(tmp_path)
    assert (tmp_path / "images" / "photo.jpg").exists()


def test_multiple_types_organized(tmp_path: Path):
    """When a folder contains multiple file types, each file should
    be moved to the correct subfolder independently. This tests that
    the function handles a realistic mix of files correctly."""
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "clip.mp4").touch()
    summary = organize_folder(tmp_path)
    assert summary["images"] == 1
    assert summary["documents"] == 1
    assert summary["videos"] == 1


# ── Average use case tests ───────────────────────────────────────
# These test realistic scenarios a normal user would encounter.

def test_extension_is_case_insensitive():
    """File extensions should match regardless of case, so .JPG
    and .jpg both go to 'images'. Users on Windows often have
    uppercase extensions from cameras or older software."""
    assert get_destination(".JPG") == "images"


def test_summary_counts_are_accurate(tmp_path: Path):
    """The summary returned by organize_folder should accurately
    count how many files went to each destination folder. Users
    rely on this summary to verify the tool did what they expected."""
    (tmp_path / "a.jpg").touch()
    (tmp_path / "b.png").touch()
    (tmp_path / "c.pdf").touch()
    summary = organize_folder(tmp_path)
    assert summary["images"] == 2
    assert summary["documents"] == 1


# ── Edge case / boundary tests ───────────────────────────────────
# These test unusual or extreme inputs that might cause the tool
# to crash or behave unexpectedly. Handling these correctly makes
# the tool safe to use in any situation.

def test_unknown_extension_is_other():
    """A file extension not in EXTENSION_MAP should fall back to
    'other' rather than raising an error. This ensures the tool
    never crashes on unexpected file types — it just puts them
    somewhere safe instead."""
    assert get_destination(".xyz") == "other"


def test_invalid_folder_raises_error():
    """Passing a path that doesn't exist should raise a ValueError
    with a clear message. This is a boundary test — the function
    should fail fast and clearly rather than producing a confusing
    low-level error from Python's file system layer."""
    with pytest.raises(ValueError):
        organize_folder(Path("/this/does/not/exist"))


def test_empty_folder_returns_empty_summary(tmp_path: Path):
    """Running the tool on an empty folder should succeed and
    return an empty summary, not raise an error. This is an edge
    case because most users assume a tool needs something to work
    with — but empty input should always be handled gracefully."""
    summary = organize_folder(tmp_path)
    assert summary == {}


def test_file_with_no_extension_goes_to_other(tmp_path: Path):
    """A file with no extension at all (like a README or Makefile)
    is an edge case that some tools crash on. It should be treated
    the same as an unknown extension and moved to 'other/'."""
    (tmp_path / "README").touch()
    organize_folder(tmp_path)
    assert (tmp_path / "other" / "README").exists()


def test_subfolders_are_not_moved(tmp_path: Path):
    """Existing subfolders inside the target folder should be left
    completely untouched. This is a critical edge case — if the
    user already has organized subfolders, the tool must not treat
    them as files and try to move them."""
    (tmp_path / "existing_folder").mkdir()
    summary = organize_folder(tmp_path)
    assert (tmp_path / "existing_folder").exists()
    assert summary == {}