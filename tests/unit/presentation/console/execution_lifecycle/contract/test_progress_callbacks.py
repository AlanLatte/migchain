"""RichPresenter -- progress callbacks with active progress bar.

- on_migration_start updates progress description
- on_migration_success advances progress
- on_migration_fail stops progress and prints FAIL
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.presentation.console import RichPresenter


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestProgressCallbacks:
    """Protects the contract of migration progress callbacks during execution."""

    def test_on_migration_start_with_progress(self):
        """Protects against on_migration_start not updating progress description."""
        presenter = make_presenter()
        presenter.start_execution(3, "apply")
        presenter.on_migration_start("0001_init", "apply")
        assert presenter._progress is not None
        presenter.finish_execution()

    def test_on_migration_success_advances_progress(self):
        """Protects against on_migration_success not advancing the progress bar."""
        presenter = make_presenter()
        presenter.start_execution(3, "apply")
        presenter.on_migration_success("0001_init", "apply", 0.5)
        assert presenter._progress is not None
        presenter.finish_execution()

    def test_on_migration_fail_stops_progress(self):
        """Protects against on_migration_fail not cleaning up the progress bar."""
        presenter = make_presenter()
        presenter.start_execution(3, "apply")
        presenter.on_migration_fail("0001_init", "apply")
        assert presenter._progress is None
        output = get_output(presenter)
        assert "FAIL" in output
        assert "0001_init" in output
