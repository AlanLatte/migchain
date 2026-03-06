"""MigrationAnalyzer.get_migration_domain -- domain extraction.

- auth/users/m.py relative to root -> "auth"
- billing/plans/inserters/m.py -> "billing"
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestExtractsDomainFromPath:
    """Protects the contract: first path component relative to root is the domain."""

    def test_returns_first_path_component(
        self,
        schema_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against wrong segment being returned as domain."""
        result = MigrationAnalyzer.get_migration_domain(
            schema_migration,
            migrations_root,
        )

        assert result == "auth"

    def test_billing_domain(
        self,
        inserter_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against inserter subdirectory leaking into domain name."""
        result = MigrationAnalyzer.get_migration_domain(
            inserter_migration,
            migrations_root,
        )

        assert result == "billing"
