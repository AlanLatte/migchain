"""PlainPresenter.prompt_scaffold -- выбор существующей поддиректории.

- При наличии существующих поддиректорий пользователь может выбрать по номеру
- Выбор номера существующей поддиректории возвращает её имя
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldSelectExistingSubdir:
    """Защищает выбор существующей поддиректории по индексу."""

    def test_selects_existing_subdirectory_by_index(self):
        """Защищает от ошибки при выборе существующей поддиректории по номеру."""
        presenter = PlainPresenter()
        inputs = iter(["2", "auth", "1", "add-column"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={"auth": ["users", "roles"]},
            )

        assert result.scaffold_type == "table"
        assert result.subdirectory == "users"
        assert result.description == "add-column"
