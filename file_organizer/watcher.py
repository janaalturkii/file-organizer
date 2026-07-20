"""
Watch mode for the file organizer.

Watches a folder for new/modified files and automatically organizes them,
with a debounce so rapid successive events (e.g. a bulk copy) don't
trigger the organizer dozens of times in a row.
"""

import logging
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class DebouncedOrganizerHandler(FileSystemEventHandler):
    """
    Reacts to file system events and schedules an organize run
    after a short quiet period (the debounce window).
    """

    def __init__(self, organize_callback, debounce_seconds: float = 2.0):
        super().__init__()
        self.organize_callback = organize_callback
        self.debounce_seconds = debounce_seconds
        self._timer = None
        self._lock = threading.Lock()
        self._organizing = False  # True while organize_callback() is actively running

    def _schedule_organize(self):
        # Every new event cancels the old timer and starts a fresh one.
        # This means organize() only fires once things go quiet.
        with self._lock:
            if self._organizing:
                # This event is almost certainly caused by organize_callback()
                # moving files (e.g. out of the watched top-level folder into
                # a subfolder) — not new user activity. Ignore it so the
                # organize pass doesn't trigger another pass of itself.
                logger.debug("Ignoring event during active organize pass.")
                return
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._run_organize)
            self._timer.daemon = True
            self._timer.start()

    def _run_organize(self):
        logger.info("Debounce period elapsed, running organize pass.")
        with self._lock:
            self._organizing = True
        try:
            self.organize_callback()
        except Exception:
            # Intentionally broad: this runs on a background Timer thread.
            # An uncaught exception here would silently kill the thread —
            # watch mode would look alive but stop organizing with no
            # visible error. Catch broadly, log with traceback, keep watching.
            logger.exception("Error while organizing during watch mode.")
        finally:
            with self._lock:
                self._organizing = False

    def on_created(self, event):
        # Note: we don't pass event.src_path to the callback — organize_callback()
        # always re-scans the folder fresh when the debounce timer fires, so a
        # file deleted before then is simply absent from that scan. No stale-path bug.
        if not event.is_directory:
            logger.debug("Detected new file: %s", event.src_path)
            self._schedule_organize()

    def on_moved(self, event):
        if not event.is_directory:
            logger.debug("Detected moved file: %s", event.dest_path)
            self._schedule_organize()


def watch_folder(folder: Path, organize_callback, debounce_seconds: float = 2.0):
    """
    Watch `folder` for changes and call organize_callback() after each
    debounce period. Blocks until interrupted with Ctrl+C.
    """
    event_handler = DebouncedOrganizerHandler(organize_callback, debounce_seconds)
    observer = Observer()
    observer.schedule(event_handler, str(folder), recursive=False)
    observer.start()
    logger.info("Watching %s for changes (Ctrl+C to stop)...", folder)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watch mode...")
    finally:
        # Always stop and join — this is the "no leaking file handles" part
        # of the acceptance criteria. Without this, the OS-level watcher
        # thread can keep running after your program exits.
        observer.stop()
        observer.join()