"""PlainPresenter.prompt_scaffold -- выбор корневой директории.

- При выборе номера "(root)" subdirectory устанавливается в пустую строку
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldRootSubdir:
    """Защищает ветку выбора корневой директории."""

    def test_root_subdirectory_selection(self):
        """Защищает от потери ветки root-поддиректории."""
        presenter = PlainPresenter()
        inputs = iter(["2", "auth", "4", "add-trigger"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={"auth": ["users", "roles"]},
            )

        assert result.subdirectory == ""
