import logging
from file_organizer.cli import setup_logging


def test_default_sets_info_level():
    """No flags passed -> should default to INFO level."""
    setup_logging(quiet=False, verbose=False)
    assert logging.getLogger().level == logging.INFO


def test_quiet_sets_warning_level():
    """--quiet -> should set level to WARNING."""
    setup_logging(quiet=True, verbose=False)
    assert logging.getLogger().level == logging.WARNING


def test_verbose_sets_debug_level():
    """--verbose -> should set level to DEBUG."""
    setup_logging(quiet=False, verbose=True)
    assert logging.getLogger().level == logging.DEBUG