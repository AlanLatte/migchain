"""PlainPresenter.prompt_scaffold -- тип "domain".

- При выборе "1" возвращает scaffold_type="domain"
- Запрашивает только имя домена без subdirectory и description
"""

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestPromptScaffoldDomain:
    """Защищает сценарий создания нового домена через prompt_scaffold."""

    def test_returns_domain_scaffold_request(self):
        """Защищает от потери ветки scaffold_type=domain."""
        presenter = PlainPresenter()
        inputs = iter(["1", "payments"])

        with patch("builtins.input", side_effect=inputs):
            result = presenter.prompt_scaffold(
                existing_domains=["auth"],
                domain_subdirectories={},
            )

        assert result.scaffold_type == "domain"
        assert result.domain == "payments"
