"""key_menu -- возврат значения по нажатию клавиши.

- нажатие зарегистрированной клавиши возвращает соответствующее значение
- меню отрисовывается в stdout перед ожиданием ввода
- после выбора меню очищается ANSI-кодами
"""

from io import StringIO
from unittest.mock import MagicMock, patch

from migchain.presentation.menu import MenuGroup, MenuItem, key_menu


def _patch_termios():
    """Создает мок termios с корректным error-классом."""
    mock = MagicMock()
    mock.error = OSError
    return mock


_MENU_PATCHES = [
    patch("sys.stdout", new_callable=StringIO),
    patch("sys.stdin"),
    patch("migchain.presentation.menu.termios", new_callable=_patch_termios),
    patch("migchain.presentation.menu._read_key", return_value="a"),
]


class TestReturnsSelectedValue:
    """Защищает контракт возврата значения при нажатии зарегистрированной клавиши."""

    @patch("migchain.presentation.menu._read_key", return_value="a")
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_returns_value_for_registered_key(self, *mocks):
        """Защищает от потери значения при корректном нажатии клавиши."""
        mocks[1].fileno.return_value = 0
        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        result = key_menu(groups)

        assert result == "apply"

    @patch("migchain.presentation.menu._read_key", return_value="r")
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_returns_value_with_title(self, *mocks):
        """Защищает от ошибки отрисовки, когда задан заголовок меню."""
        mocks[1].fileno.return_value = 0
        groups = (MenuGroup("Actions", (MenuItem("r", "{r}un", "run"),)),)

        result = key_menu(groups, title="Pick action")

        assert result == "run"

    @patch("migchain.presentation.menu._read_key", return_value="p")
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_renders_menu_with_group_without_title(self, *mocks):
        """Защищает от пропуска пунктов меню в группе без заголовка."""
        mocks[1].fileno.return_value = 0
        groups = (MenuGroup("", (MenuItem("p", "{p}rod", "production"),)),)

        result = key_menu(groups)

        assert result == "production"


class TestClearsMenuAfterSelection:
    """Защищает контракт очистки меню ANSI-кодами после выбора."""

    @patch("migchain.presentation.menu._read_key", return_value="a")
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_stdout_contains_ansi_clear(self, mock_stdout, mock_stdin, *_):
        """Защищает от отсутствия ANSI-очистки после выбора пункта."""
        mock_stdin.fileno.return_value = 0
        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        key_menu(groups)

        output = mock_stdout.getvalue()
        assert "\033[" in output
        assert "\033[J" in output
