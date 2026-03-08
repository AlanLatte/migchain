"""OPERATION_MENU, ENVIRONMENT_MENU -- реестры пунктов меню.

- OPERATION_MENU содержит группы Migrations, Rollback, Tools
- ENVIRONMENT_MENU содержит группу с пустым заголовком (production, testing, testing-gw)
- все ожидаемые значения присутствуют в реестрах
"""

from migchain.presentation.menu import ENVIRONMENT_MENU, OPERATION_MENU


class TestOperationMenu:
    """Защищает полноту реестра операций."""

    def test_contains_three_groups(self):
        """Защищает от случайного удаления группы из OPERATION_MENU."""
        assert len(OPERATION_MENU) == 3

    def test_group_titles(self):
        """Защищает от переименования групп операций."""
        titles = [g.title for g in OPERATION_MENU]

        assert titles == ["Migrations", "Rollback", "Tools"]

    def test_all_operation_values(self):
        """Защищает от потери пунктов меню операций."""
        values = {item.value for group in OPERATION_MENU for item in group.items}

        expected = {
            "apply",
            "new",
            "rollback",
            "rollback-one",
            "rollback-latest",
            "reload",
            "optimize",
        }
        assert values == expected

    def test_all_operation_keys(self):
        """Защищает от коллизии клавиш в OPERATION_MENU."""
        keys = [item.key for group in OPERATION_MENU for item in group.items]

        assert len(keys) == len(set(keys))


class TestEnvironmentMenu:
    """Защищает полноту реестра окружений."""

    def test_contains_one_group(self):
        """Защищает от случайного добавления/удаления групп окружений."""
        assert len(ENVIRONMENT_MENU) == 1

    def test_group_has_empty_title(self):
        """Защищает от появления заголовка у группы окружений."""
        assert ENVIRONMENT_MENU[0].title == ""

    def test_all_environment_values(self):
        """Защищает от потери пунктов меню окружений."""
        values = {item.value for item in ENVIRONMENT_MENU[0].items}

        expected = {"production", "testing", "testing-gw"}
        assert values == expected

    def test_all_environment_keys(self):
        """Защищает от коллизии клавиш в ENVIRONMENT_MENU."""
        keys = [item.key for item in ENVIRONMENT_MENU[0].items]

        assert len(keys) == len(set(keys))
