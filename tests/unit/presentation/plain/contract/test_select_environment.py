"""PlainPresenter.select_environment -- делегирование в key_menu.

- Вызывает key_menu с ENVIRONMENT_MENU и заголовком "Environment"
- Возвращает результат key_menu
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestSelectEnvironment:
    """Защищает делегирование select_environment в key_menu."""

    def test_delegates_to_key_menu(self):
        """Защищает от нарушения контракта вызова key_menu с ENVIRONMENT_MENU."""
        presenter = PlainPresenter()
        with patch(
            "migchain.presentation.plain.key_menu",
            return_value="production",
        ) as mock_menu:
            result = presenter.select_environment()

        assert result == "production"
        mock_menu.assert_called_once()
        args = mock_menu.call_args
        assert args[0][1] == "Environment"
