"""RichPresenter -- progress bar lifecycle.

- start_execution creates progress
- finish_execution clears progress
- finish without start is safe
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.presentation.console import RichPresenter


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


class TestProgressBar:
    """Protects the contract of progress bar creation and teardown lifecycle."""

    def test_start_creates_progress(self):
        """Protects against start_execution not initializing the progress bar."""
        presenter = make_presenter()
        presenter.start_execution(5, "apply")
        assert presenter._progress is not None
        presenter.finish_execution()

    def test_finish_clears_progress(self):
        """Protects against finish_execution not cleaning up the progress bar."""
        presenter = make_presenter()
        presenter.start_execution(5, "apply")
        presenter.finish_execution()
        assert presenter._progress is None

    def test_finish_without_start_is_safe(self):
        """Protects against finish_execution raising when no progress was started."""
        presenter = make_presenter()
        presenter.finish_execution()
        assert presenter._progress is None
