"""PlainPresenter.prompt_scaffold -- невалидный выбор типа.

- При вводе несуществующего номера выбирается freeform по умолчанию
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldInvalidChoice:
    """Защищает fallback на freeform при невалидном выборе типа."""

    def test_defaults_to_freeform_on_invalid_choice(self):
        """Защищает от ошибки при вводе несуществующего номера типа миграции."""
        presenter = PlainPresenter()
        inputs = iter(["9", "auth", "tables", "fix-index"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=[],
                domain_subdirectories={},
            )

        assert result.scaffold_type == "freeform"
        assert result.domain == "auth"
