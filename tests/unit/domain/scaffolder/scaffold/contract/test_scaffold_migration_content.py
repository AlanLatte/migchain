"""MigrationScaffolder._scaffold_migration -- содержимое файла миграции.

- Создаёт файл с шаблоном step с пустыми SQL-блоками
- Содержит docstring из description
- description с дефисами -> capitalize с пробелами в docstring
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestScaffoldMigrationContent:
    """Защищает контракт: _scaffold_migration создаёт валидный шаблон миграции."""

    def test_file_contains_step_template(self, migrations_root: Path) -> None:
        """Защищает от пустого или некорректного шаблона step."""
        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
            description="create-users",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "from yoyo import step" in content
        assert "steps = [" in content
        assert "step(" in content

    def test_docstring_capitalizes_description(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от неверного форматирования docstring из description."""
        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
            description="create-users-table",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "Create users table" in content
