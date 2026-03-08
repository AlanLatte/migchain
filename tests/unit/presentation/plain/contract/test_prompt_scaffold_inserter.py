"""PlainPresenter.prompt_scaffold -- тип "inserter".

- При выборе "3" возвращает scaffold_type="inserter"
- Запрашивает домен, поддиректорию и описание
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldInserter:
    """Защищает сценарий создания inserter-миграции через prompt_scaffold."""

    def test_returns_inserter_scaffold_request(self):
        """Защищает от потери ветки scaffold_type=inserter."""
        presenter = PlainPresenter()
        inputs = iter(["3", "billing", "invoices", "seed-data"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["billing"],
                domain_subdirectories={},
            )

        assert result.scaffold_type == "inserter"
        assert result.domain == "billing"
        assert result.subdirectory == "invoices"
        assert result.description == "seed-data"
