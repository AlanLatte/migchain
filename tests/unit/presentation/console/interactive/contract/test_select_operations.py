"""RichPresenter.select_operation / select_environment -- делегирование в key_menu.

- select_operation вызывает key_menu с OPERATION_MENU
- select_environment вызывает key_menu с ENVIRONMENT_MENU
- возвращает значение из key_menu
"""
# pylint: disable=protected-access

from unittest.mock import patch

from migchain.presentation.console import RichPresenter


class TestSelectOperations:
    """Защищает контракт делегирования интерактивного выбора в key_menu."""

    def test_select_operation_delegates_to_key_menu(self):
        """Защищает от потери делегирования select_operation в key_menu."""
        presenter = RichPresenter()
        with patch(
            "migchain.presentation.console.key_menu",
            return_value="apply",
        ) as mock_menu:
            result = presenter.select_operation()

        assert result == "apply"
        mock_menu.assert_called_once()

    def test_select_environment_delegates_to_key_menu(self):
        """Защищает от потери делегирования select_environment в key_menu."""
        presenter = RichPresenter()
        with patch(
            "migchain.presentation.console.key_menu",
            return_value="testing",
        ) as mock_menu:
            result = presenter.select_environment()

        assert result == "testing"
        mock_menu.assert_called_once()

    def test_select_operation_returns_none_when_key_menu_returns_none(self):
        """Защищает от ошибки при отсутствии TTY (key_menu возвращает None)."""
        presenter = RichPresenter()
        with patch(
            "migchain.presentation.console.key_menu",
            return_value=None,
        ):
            result = presenter.select_operation()

        assert result is None
