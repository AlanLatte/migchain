"""MigrationAnalyzer.get_migration_full_path -- boundary inputs.

- empty path -> "unknown"
- external path -> "external"
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestEmptyAndExternal:
    """Protects the fallback behavior when path is empty or outside root."""

    def test_empty_path_returns_unknown(self, migrations_root: Path) -> None:
        """Protects against crash on empty path string."""
        migration = FakeMigration(id="x", path="")

        result = MigrationAnalyzer.get_migration_full_path(migration, migrations_root)

        assert result == "unknown"

    def test_external_returns_external(self, migrations_root: Path) -> None:
        """Protects against ValueError when path is outside migrations root."""
        migration = FakeMigration(id="x", path="/some/other/place/m.py")

        result = MigrationAnalyzer.get_migration_full_path(migration, migrations_root)

        assert result == "external"
