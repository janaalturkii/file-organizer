"""
Unit tests for file_organizer/watcher.py

We do NOT spin up a real watchdog Observer or touch the real file system
here — that's slow, flaky, and mostly just testing watchdog's own code,
not ours. Instead we test DebouncedOrganizerHandler directly, using a
short debounce_seconds so tests run fast, and fake "event" objects
instead of real file system events.
"""

import time
import unittest
from unittest.mock import MagicMock

from file_organizer.watcher import DebouncedOrganizerHandler


class FakeEvent:
    """
    A minimal stand-in for watchdog's real event objects.
    We only need the two attributes DebouncedOrganizerHandler reads:
    is_directory, and src_path/dest_path (for logging only).
    """

    def __init__(self, path="some/file.txt", is_directory=False):
        self.src_path = path
        self.dest_path = path
        self.is_directory = is_directory


class TestDebouncedOrganizerHandler(unittest.TestCase):

    def test_schedule_organize_calls_callback_after_debounce(self):
        """A single event should result in organize_callback being called
        once the debounce window has elapsed."""
        callback = MagicMock()
        handler = DebouncedOrganizerHandler(callback, debounce_seconds=0.1)

        handler._schedule_organize()

        callback.assert_not_called()

        time.sleep(0.2)

        callback.assert_called_once()

    def test_rapid_events_only_trigger_one_organize_call(self):
        """Multiple events arriving in quick succession (faster than the
        debounce window) should collapse into a single organize_callback
        call — this is the whole point of debouncing."""
        callback = MagicMock()
        handler = DebouncedOrganizerHandler(callback, debounce_seconds=0.2)

        for _ in range(5):
            handler._schedule_organize()
            time.sleep(0.05)

        callback.assert_not_called()

        time.sleep(0.3)

        callback.assert_called_once()

    def test_on_created_ignores_directories(self):
        """Directory creation events should NOT trigger an organize pass —
        we only care about files landing in the watched folder."""
        callback = MagicMock()
        handler = DebouncedOrganizerHandler(callback, debounce_seconds=0.05)

        dir_event = FakeEvent(path="some/new_folder", is_directory=True)
        handler.on_created(dir_event)

        time.sleep(0.1)
        callback.assert_not_called()

    def test_on_created_schedules_for_files(self):
        """A file creation event should schedule an organize pass."""
        callback = MagicMock()
        handler = DebouncedOrganizerHandler(callback, debounce_seconds=0.05)

        file_event = FakeEvent(path="some/new_file.txt", is_directory=False)
        handler.on_created(file_event)

        time.sleep(0.1)
        callback.assert_called_once()

    def test_on_moved_schedules_for_files(self):
        """A file move/rename event should also schedule an organize pass
        (e.g. when a download finishes and the browser renames a .crdownload
        file to its final name)."""
        callback = MagicMock()
        handler = DebouncedOrganizerHandler(callback, debounce_seconds=0.05)

        move_event = FakeEvent(path="some/renamed_file.txt", is_directory=False)
        handler.on_moved(move_event)

        time.sleep(0.1)
        callback.assert_called_once()

    def test_exception_in_callback_does_not_crash_handler(self):
        """If organize_callback raises (e.g. a permissions error mid-move),
        the handler should log it and stay alive — not blow up the whole
        watch process."""
        callback = MagicMock(side_effect=RuntimeError("boom"))
        handler = DebouncedOrganizerHandler(callback, debounce_seconds=0.05)

        handler._schedule_organize()
        time.sleep(0.1)

        callback.assert_called_once()


if __name__ == "__main__":
    unittest.main()