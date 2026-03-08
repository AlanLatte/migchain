"""resolve_environment -- интерактивный выбор окружения.

- production -> args.testing остается False
- testing -> args.testing = True
- testing-gw -> args.testing = True, запрашивает gw_count и gw_template
- non-DB операция -> ранний возврат без промпта
"""

from unittest.mock import MagicMock, patch

from migchain.presentation.cli import resolve_environment


class TestProductionChoice:
    """Защищает контракт выбора production -- testing не активируется."""

    def test_production_keeps_testing_false(self, base_namespace):
        """Защищает от ошибочной активации testing при выборе production."""
        presenter = MagicMock()
        presenter.select_environment.return_value = "production"

        resolve_environment(base_namespace, "apply", presenter)

        assert base_namespace.testing is False


class TestTestingChoice:
    """Защищает контракт выбора testing -- активируется флаг testing."""

    def test_testing_sets_flag(self, base_namespace):
        """Защищает от потери установки testing=True при выборе testing."""
        presenter = MagicMock()
        presenter.select_environment.return_value = "testing"

        resolve_environment(base_namespace, "apply", presenter)

        assert base_namespace.testing is True


class TestTestingGwChoice:
    """Защищает контракт выбора testing-gw -- запрос gateway параметров."""

    def test_testing_gw_prompts_for_gateway_settings(self, base_namespace):
        """Защищает от потери промпта gateway параметров при выборе testing-gw."""
        presenter = MagicMock()
        presenter.select_environment.return_value = "testing-gw"

        with patch("builtins.input", side_effect=["8", "gw_db_{i}"]):
            resolve_environment(base_namespace, "apply", presenter)

        assert base_namespace.testing is True
        assert base_namespace.gw_count == 8
        assert base_namespace.gw_template == "gw_db_{i}"

    def test_testing_gw_uses_defaults(self, base_namespace):
        """Защищает от ошибки при пустом вводе -- используются значения по умолчанию."""
        presenter = MagicMock()
        presenter.select_environment.return_value = "testing-gw"

        with patch("builtins.input", side_effect=["", ""]):
            resolve_environment(base_namespace, "apply", presenter)

        assert base_namespace.testing is True
        assert base_namespace.gw_count == 4
        assert base_namespace.gw_template is None


class TestNonDbOperationSkips:
    """Защищает ранний возврат для операций без БД."""

    def test_non_db_operation_skips_prompt(self, base_namespace):
        """Защищает от ненужного промпта окружения для операции 'new'."""
        presenter = MagicMock()

        resolve_environment(base_namespace, "new", presenter)

        presenter.select_environment.assert_not_called()
        assert base_namespace.testing is False
