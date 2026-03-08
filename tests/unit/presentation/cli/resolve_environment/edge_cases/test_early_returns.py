"""resolve_environment -- ранние возвраты при уже установленных флагах.

- args.testing=True -> возврат без промпта
- args.dry_run=True -> возврат без промпта
- presenter=None -> возврат без ошибки
"""

from unittest.mock import MagicMock

from migchain.presentation.cli import resolve_environment


class TestAlreadyTestingSkips:
    """Защищает ранний возврат когда testing уже активен."""

    def test_already_testing_skips_prompt(self, base_namespace):
        """Защищает от повторного промпта окружения при уже активном testing."""
        base_namespace.testing = True
        presenter = MagicMock()

        resolve_environment(base_namespace, "apply", presenter)

        presenter.select_environment.assert_not_called()


class TestNoPresenterSkips:
    """Защищает ранний возврат при отсутствии presenter."""

    def test_none_presenter_skips_without_error(self, base_namespace):
        """Защищает от ошибки при вызове без presenter."""
        resolve_environment(base_namespace, "apply", presenter=None)

        assert base_namespace.testing is False
