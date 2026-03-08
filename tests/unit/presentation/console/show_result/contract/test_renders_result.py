"""RichPresenter.show_result -- отображение результата.

- сообщение отображается в выводе
- вывод содержит текст сообщения
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


class TestRendersResult:
    """Защищает контракт отображения финального сообщения через show_result."""

    def test_message_appears_in_output(self):
        """Защищает от потери текста сообщения в выводе show_result."""
        presenter = make_presenter()
        presenter.show_result("Applied 3 migration(s)")
        output = get_output(presenter)

        assert "Applied 3 migration(s)" in output
