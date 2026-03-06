"""MigrationAnalyzer.analyze_structure -- aggregation.

- single schema -> total=1, schema_count=1, domain tracked
- mixed schema+inserter -> correct counts per domain
- domain migration_ids populated
- schema_paths and inserter_paths tracked
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestAggregatesStats:
    """Protects the aggregation contract: counts, ids,
    and paths are correctly accumulated."""

    def test_single_schema(
        self,
        schema_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against off-by-one in total
        and schema_count for a single migration."""
        result = MigrationAnalyzer.analyze_structure(
            [schema_migration],
            migrations_root,
        )

        assert result.total == 1
        assert result.schema_count == 1
        assert result.inserter_count == 0
        assert "auth" in result.domains

    def test_mixed_migrations(
        self,
        schema_migration: FakeMigration,
        inserter_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against cross-domain count leaking between schema and inserter."""
        result = MigrationAnalyzer.analyze_structure(
            [schema_migration, inserter_migration],
            migrations_root,
        )

        assert result.total == 2
        assert result.schema_count == 1
        assert result.inserter_count == 1
        assert result.domains["auth"].schema_count == 1
        assert result.domains["billing"].inserter_count == 1

    def test_domain_stats_migration_ids(
        self,
        schema_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against migration id not being recorded in domain stats."""
        result = MigrationAnalyzer.analyze_structure(
            [schema_migration],
            migrations_root,
        )

        assert schema_migration.id in result.domains["auth"].migration_ids

    def test_schema_paths_tracked(
        self,
        schema_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against schema path not appearing in schema_paths set."""
        result = MigrationAnalyzer.analyze_structure(
            [schema_migration],
            migrations_root,
        )

        assert "auth/users" in result.schema_paths

    def test_inserter_paths_tracked(
        self,
        inserter_migration: FakeMigration,
        migrations_root: Path,
    ) -> None:
        """Protects against inserter path not appearing in inserter_paths set."""
        result = MigrationAnalyzer.analyze_structure(
            [inserter_migration],
            migrations_root,
        )

        assert "billing/plans/inserters" in result.inserter_paths

    def test_multiple_same_domain(self, migrations_root: Path) -> None:
        """Protects against counter reset when two migrations share the same domain."""
        m1 = FakeMigration(
            id="m1",
            path=str(migrations_root / "auth" / "users" / "m1.py"),
        )
        m2 = FakeMigration(
            id="m2",
            path=str(migrations_root / "auth" / "roles" / "m2.py"),
        )

        result = MigrationAnalyzer.analyze_structure([m1, m2], migrations_root)

        assert result.domains["auth"].schema_count == 2
