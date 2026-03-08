"""PlainPresenter.prompt_scaffold -- ручной ввод поддиректории.

- При выборе номера "(enter manually)" запрашивается имя поддиректории вручную
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldManualSubdir:
    """Защищает ветку ручного ввода поддиректории при наличии существующих."""

    def test_manual_subdirectory_entry(self):
        """Защищает от потери ветки ручного ввода поддиректории."""
        presenter = PlainPresenter()
        inputs = iter(["2", "auth", "3", "permissions", "create-table"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={"auth": ["users", "roles"]},
            )

        assert result.subdirectory == "permissions"
