"""PlainPresenter.select_operation -- делегирование в key_menu.

- Вызывает key_menu с OPERATION_MENU и заголовком "MigChain"
- Возвращает результат key_menu
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestSelectOperation:
    """Защищает делегирование select_operation в key_menu."""

    def test_delegates_to_key_menu(self):
        """Защищает от нарушения контракта вызова key_menu с OPERATION_MENU."""
        presenter = PlainPresenter()
        with patch(
            "migchain.presentation.plain.key_menu",
            return_value="apply",
        ) as mock_menu:
            result = presenter.select_operation()

        assert result == "apply"
        mock_menu.assert_called_once()
        assert mock_menu.call_args[0][1] == "MigChain"
