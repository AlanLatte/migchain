"""MigrationScaffolder.scaffold -- диспетчеризация по типу domain.

- scaffold_type="domain" -> вызывает _scaffold_domain
- Создаётся файл со схемой CREATE SCHEMA
- Возвращает ScaffoldResult с корректным file_path и migration_id
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestDispatchesDomainType:
    """Защищает контракт: scaffold_type='domain' делегирует в _scaffold_domain."""

    def test_creates_schema_migration_file(self, migrations_root: Path) -> None:
        """Защищает от потери маршрутизации domain-типа в handlers."""
        request = ScaffoldRequest(scaffold_type="domain", domain="auth")

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.exists()
        content = result.file_path.read_text(encoding="utf-8")
        assert "CREATE SCHEMA IF NOT EXISTS auth" in content
        assert "DROP SCHEMA IF EXISTS auth CASCADE" in content

    def test_result_migration_id_matches_filename(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от рассинхронизации migration_id и имени файла."""
        request = ScaffoldRequest(scaffold_type="domain", domain="billing")

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.name == f"{result.migration_id}.py"
