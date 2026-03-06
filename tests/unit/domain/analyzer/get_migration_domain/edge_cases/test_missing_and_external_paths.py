"""MigrationAnalyzer.get_migration_domain -- boundary inputs.

- empty path -> "unknown"
- external path -> "external"
- root-level file -> filename as domain
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestMissingAndExternalPaths:
    """Protects the fallback behavior for non-standard migration paths."""

    def test_empty_path_returns_unknown(self, migrations_root: Path) -> None:
        """Protects against crash on empty path string."""
        migration = FakeMigration(id="x", path="")

        result = MigrationAnalyzer.get_migration_domain(migration, migrations_root)

        assert result == "unknown"

    def test_external_path_returns_external(self, migrations_root: Path) -> None:
        """Protects against ValueError when path is outside migrations root."""
        migration = FakeMigration(id="x", path="/some/other/place/m.py")

        result = MigrationAnalyzer.get_migration_domain(migration, migrations_root)

        assert result == "external"

    def test_root_level_file_returns_filename(self, migrations_root: Path) -> None:
        """Protects against IndexError when file sits directly in root."""
        migration = FakeMigration(
            id="x",
            path=str(migrations_root / "m.py"),
        )

        result = MigrationAnalyzer.get_migration_domain(migration, migrations_root)

        assert result == "m.py"
