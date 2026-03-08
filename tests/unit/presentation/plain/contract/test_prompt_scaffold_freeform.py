"""PlainPresenter.prompt_scaffold -- тип "freeform".

- При выборе "4" возвращает scaffold_type="freeform"
- Запрашивает домен, поддиректорию и описание
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldFreeform:
    """Защищает сценарий создания произвольной миграции через prompt_scaffold."""

    def test_returns_freeform_scaffold_request(self):
        """Защищает от потери ветки scaffold_type=freeform."""
        presenter = PlainPresenter()
        inputs = iter(["4", "core", "misc", "custom-change"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=[],
                domain_subdirectories={},
            )

        assert result.scaffold_type == "freeform"
        assert result.domain == "core"
        assert result.subdirectory == "misc"
        assert result.description == "custom-change"
