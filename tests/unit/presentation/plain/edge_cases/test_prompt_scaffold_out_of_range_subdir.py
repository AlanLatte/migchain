"""PlainPresenter.prompt_scaffold -- индекс поддиректории вне диапазона.

- При вводе числового индекса вне допустимого диапазона используется сырой ввод
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldOutOfRangeSubdir:
    """Защищает fallback при индексе поддиректории вне диапазона."""

    def test_out_of_range_index_falls_back_to_raw_input(self):
        """Защищает от ошибки при индексе поддиректории больше допустимого."""
        presenter = PlainPresenter()
        inputs = iter(["2", "auth", "99", "add-constraint"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={"auth": ["users", "roles"]},
            )

        assert result.subdirectory == "99"
