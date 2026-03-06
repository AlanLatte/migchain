"""MigrationAnalyzer.get_migration_full_path -- relative parent extraction.

- auth/users/m.py -> "auth/users"
- billing/plans/inserters/m.py -> "billing/plans/inserters"
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestReturnsRelativeParent:
    """Protects the contract: relative parent directory is returned without filename."""

    def test_schema_path(
        self,
        schema_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against filename leaking into the full path result."""
        result = MigrationAnalyzer.get_migration_full_path(
            schema_migration,
            migrations_root,
        )

        assert result == "auth/users"

    def test_inserter_path(
        self,
        inserter_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against inserters subdirectory being stripped from the path."""
        result = MigrationAnalyzer.get_migration_full_path(
            inserter_migration,
            migrations_root,
        )

        assert result == "billing/plans/inserters"
