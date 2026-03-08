"""PlainPresenter.prompt_scaffold -- тип "table".

- При выборе "2" возвращает scaffold_type="table"
- Запрашивает домен, поддиректорию и описание
- При отсутствии существующих поддиректорий запрашивает ввод вручную
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldTable:
    """Защищает сценарий создания табличной миграции через prompt_scaffold."""

    def test_returns_table_scaffold_request_no_existing_subdirs(self):
        """Защищает от потери ветки scaffold_type=table."""
        presenter = PlainPresenter()
        inputs = iter(["2", "auth", "users", "create-table"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={},
            )

        assert result.scaffold_type == "table"
        assert result.domain == "auth"
        assert result.subdirectory == "users"
        assert result.description == "create-table"
