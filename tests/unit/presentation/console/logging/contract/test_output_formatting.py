"""RichPresenter -- logging output.

- info() includes message text
- warning() includes message text
- error() includes message text
- debug() hidden at verbosity < 2
- debug() shown at verbosity >= 2
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


class TestOutputFormatting:
    """Protects the contract of logging output methods and verbosity gating."""

    def test_info(self):
        """Protects against info() not including the message text in output."""
        presenter = make_presenter()
        presenter.info("test message")
        output = get_output(presenter)
        assert "test message" in output

    def test_warning(self):
        """Protects against warning() not including the message text in output."""
        presenter = make_presenter()
        presenter.warning("warn msg")
        output = get_output(presenter)
        assert "warn msg" in output

    def test_error(self):
        """Protects against error() not including the message text in output."""
        presenter = make_presenter()
        presenter.error("error msg")
        output = get_output(presenter)
        assert "error msg" in output

    def test_debug_hidden(self):
        """Protects against debug messages leaking through at low verbosity."""
        presenter = make_presenter()
        presenter._verbosity = 1
        presenter.debug("debug msg")
        output = get_output(presenter)
        assert "debug msg" not in output

    def test_debug_shown(self):
        """Protects against debug messages being suppressed at high verbosity."""
        presenter = make_presenter()
        presenter._verbosity = 2
        presenter.debug("debug msg")
        output = get_output(presenter)
        assert "debug msg" in output

    def test_setup_stores_verbosity(self):
        """Protects against setup() not persisting the verbosity level."""
        presenter = make_presenter()
        presenter.setup(2)
        assert presenter._verbosity == 2
