"""_read_key -- чтение одиночного нажатия клавиши из stdin.

- обычный символ возвращается как есть
- escape-последовательность (\x1b) потребляется целиком и возвращает пустую строку
- termios восстанавливается в finally-блоке после чтения
"""

from unittest.mock import patch

from migchain.presentation.menu import _read_key


class TestReadsNormalChar:
    """Защищает контракт чтения обычного символа."""

    @patch("migchain.presentation.menu.termios")
    @patch("migchain.presentation.menu.tty")
    @patch("sys.stdin")
    def test_returns_normal_character(
        self,
        mock_stdin,
        _mock_tty,
        mock_termios,
    ):
        """Защищает от потери символа при чтении обычной клавиши."""
        mock_stdin.fileno.return_value = 0
        mock_termios.tcgetattr.return_value = [1, 2, 3]
        mock_stdin.read.return_value = "a"

        result = _read_key()

        assert result == "a"


class TestConsumesEscapeSequence:
    """Защищает контракт потребления escape-последовательностей."""

    @patch("migchain.presentation.menu._fd_select")
    @patch("migchain.presentation.menu.termios")
    @patch("migchain.presentation.menu.tty")
    @patch("sys.stdin")
    def test_escape_returns_empty_string(
        self,
        mock_stdin,
        _mock_tty,
        mock_termios,
        mock_fd_select,
    ):
        """Защищает от возврата частичной escape-последовательности."""
        mock_stdin.fileno.return_value = 0
        mock_termios.tcgetattr.return_value = [1, 2, 3]
        mock_stdin.read.side_effect = ["\x1b", "[", "A"]
        mock_fd_select.side_effect = [
            ([mock_stdin], [], []),
            ([mock_stdin], [], []),
            ([], [], []),
        ]

        result = _read_key()

        assert result == ""


class TestRestoresTermios:
    """Защищает контракт восстановления настроек терминала."""

    @patch("migchain.presentation.menu.termios")
    @patch("migchain.presentation.menu.tty")
    @patch("sys.stdin")
    def test_restores_terminal_on_success(
        self,
        mock_stdin,
        _mock_tty,
        mock_termios,
    ):
        """Защищает от оставления терминала в cbreak-режиме после чтения."""
        mock_stdin.fileno.return_value = 0
        old_settings = [1, 2, 3, 4]
        mock_termios.tcgetattr.return_value = old_settings
        mock_stdin.read.return_value = "x"

        _read_key()

        mock_termios.tcsetattr.assert_called_once_with(
            0,
            mock_termios.TCSADRAIN,
            old_settings,
        )

    @patch("migchain.presentation.menu.termios")
    @patch("migchain.presentation.menu.tty")
    @patch("sys.stdin")
    def test_restores_terminal_on_exception(
        self,
        mock_stdin,
        _mock_tty,
        mock_termios,
    ):
        """Защищает от оставления терминала в cbreak-режиме при ошибке."""
        mock_stdin.fileno.return_value = 0
        old_settings = [1, 2, 3, 4]
        mock_termios.tcgetattr.return_value = old_settings
        mock_stdin.read.side_effect = IOError("read error")

        try:
            _read_key()
        except IOError:
            pass

        mock_termios.tcsetattr.assert_called_once_with(
            0,
            mock_termios.TCSADRAIN,
            old_settings,
        )
