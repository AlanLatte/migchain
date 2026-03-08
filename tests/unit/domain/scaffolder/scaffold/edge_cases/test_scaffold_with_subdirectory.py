"""MigrationScaffolder.scaffold -- edge cases с поддиректориями.

- migration с subdirectory -> файл в domain/subdirectory/
- inserter с subdirectory -> файл в domain/subdirectory/inserters/
- migration без description -> default "new-migration"
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestScaffoldWithSubdirectory:
    """Защищает граничные случаи: вложенные поддиректории при scaffold."""

    def test_migration_in_subdirectory(self, migrations_root: Path) -> None:
        """Защищает от игнорирования subdirectory при создании table-миграции."""
        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
            subdirectory="users",
            description="create-table",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.parent == migrations_root / "auth" / "users"
        assert result.file_path.exists()

    def test_inserter_in_subdirectory(self, migrations_root: Path) -> None:
        """Защищает от потери subdirectory при создании inserter-миграции."""
        request = ScaffoldRequest(
            scaffold_type="inserter",
            domain="billing",
            subdirectory="plans",
            description="seed-data",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        expected_dir = migrations_root / "billing" / "plans" / "inserters"
        assert result.file_path.parent == expected_dir

    def test_migration_without_description_uses_default(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от ошибки при пустом description."""
        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "New migration" in content

    def test_inserter_without_description_uses_default(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от ошибки при пустом description для inserter."""
        request = ScaffoldRequest(
            scaffold_type="inserter",
            domain="auth",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "Insert data" in content
