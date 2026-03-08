"""key_menu -- edge cases: отсутствие TTY, Ctrl+C, 'q', неизвестные клавиши.

- _HAS_TTY=False возвращает None
- Ctrl+C (\x03) вызывает KeyboardInterrupt
- 'q' вызывает SystemExit
- неизвестные клавиши игнорируются до валидного нажатия
- termios.error при проверке TTY возвращает None
"""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from migchain.presentation.menu import MenuGroup, MenuItem, key_menu


def _patch_termios():
    """Создает мок termios с корректным error-классом."""
    mock = MagicMock()
    mock.error = OSError
    return mock


class TestNoTtyReturnsNone:
    """Защищает контракт возврата None при отсутствии TTY."""

    @patch("migchain.presentation.menu._HAS_TTY", False)
    def test_returns_none_without_tty(self):
        """Защищает от ошибки вместо None, когда TTY недоступен."""
        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        result = key_menu(groups)

        assert result is None


class TestTermiosErrorReturnsNone:
    """Защищает контракт возврата None при ошибке termios."""

    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_returns_none_on_termios_error(
        self,
        _mock_stdout,
        mock_stdin,
        mock_termios,
    ):
        """Защищает от исключения при ошибке termios.tcgetattr."""
        mock_stdin.fileno.return_value = 0
        mock_termios.tcgetattr.side_effect = OSError("not a tty")

        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        result = key_menu(groups)

        assert result is None


class TestCtrlCRaisesKeyboardInterrupt:
    """Защищает контракт прерывания по Ctrl+C."""

    @patch("migchain.presentation.menu._read_key", return_value="\x03")
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_raises_keyboard_interrupt(
        self,
        _mock_stdout,
        mock_stdin,
        _mock_termios,
        _mock_read_key,
    ):
        """Защищает от молчаливого игнорирования Ctrl+C."""
        mock_stdin.fileno.return_value = 0
        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        with pytest.raises(KeyboardInterrupt):
            key_menu(groups)


class TestQuitRaisesSystemExit:
    """Защищает контракт завершения по клавише 'q'."""

    @patch("migchain.presentation.menu._read_key", return_value="q")
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_raises_system_exit(
        self,
        _mock_stdout,
        mock_stdin,
        _mock_termios,
        _mock_read_key,
    ):
        """Защищает от продолжения работы при нажатии 'q'."""
        mock_stdin.fileno.return_value = 0
        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        with pytest.raises(SystemExit) as exc_info:
            key_menu(groups)

        assert exc_info.value.code == 0


class TestIgnoresUnknownKeys:
    """Защищает контракт игнорирования незарегистрированных клавиш."""

    @patch(
        "migchain.presentation.menu._read_key",
        side_effect=["x", "z", "a"],
    )
    @patch("migchain.presentation.menu.termios", new_callable=_patch_termios)
    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_skips_unknown_and_returns_valid(
        self,
        _mock_stdout,
        mock_stdin,
        _mock_termios,
        mock_read_key,
    ):
        """Защищает от выхода из меню при нажатии незарегистрированной клавиши."""
        mock_stdin.fileno.return_value = 0
        groups = (MenuGroup("Test", (MenuItem("a", "{a}pply", "apply"),)),)

        result = key_menu(groups)

        assert result == "apply"
        assert mock_read_key.call_count == 3
