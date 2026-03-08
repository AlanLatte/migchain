"""MigrationScaffolder.scaffold -- диспетчеризация по типам table и freeform.

- scaffold_type="table" -> fallback на _scaffold_migration
- scaffold_type="freeform" -> fallback на _scaffold_migration
- Неизвестный тип -> fallback на _scaffold_migration
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestDispatchesMigrationType:
    """Защищает контракт: неизвестные типы используют fallback."""

    def test_table_type_uses_migration_handler(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от отсутствия fallback для типа table."""
        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
            description="create-users",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.exists()
        content = result.file_path.read_text(encoding="utf-8")
        assert "from yoyo import step" in content

    def test_freeform_type_uses_migration_handler(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от отсутствия fallback для типа freeform."""
        request = ScaffoldRequest(
            scaffold_type="freeform",
            domain="auth",
            description="add-index",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.exists()
        content = result.file_path.read_text(encoding="utf-8")
        assert "from yoyo import step" in content

    def test_unknown_type_falls_back_to_migration(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от ошибки при передаче незарегистрированного типа."""
        request = ScaffoldRequest(
            scaffold_type="unknown_type",
            domain="auth",
            description="something",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.exists()
