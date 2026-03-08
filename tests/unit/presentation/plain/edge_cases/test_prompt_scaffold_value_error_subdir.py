"""PlainPresenter.prompt_scaffold -- нечисловой ввод поддиректории.

- При вводе нечислового значения для поддиректории используется как есть
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldValueErrorSubdir:
    """Защищает обработку ValueError при парсинге номера поддиректории."""

    def test_non_numeric_input_used_as_subdirectory(self):
        """Защищает от ошибки при нечисловом вводе номера поддиректории."""
        presenter = PlainPresenter()
        inputs = iter(["2", "auth", "custom-dir", "add-index"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={"auth": ["users", "roles"]},
            )

        assert result.subdirectory == "custom-dir"
