"""MigrationPlanner.filter_without_inserters -- inserter removal.

- schema-only passes through
- mixed removes inserters
- all inserters -> empty result
- schema depending on schema -> both preserved
"""

from pathlib import Path

from migchain.domain.planner import MigrationPlanner
from tests.conftest import FakeMigration


class TestRemovesInserters:
    """Protects the filter contract: inserters are removed
    while schemas pass through."""

    def test_schema_passes_through(self, schema_migration: FakeMigration) -> None:
        """Protects against schema migrations being incorrectly filtered out."""
        result = MigrationPlanner.filter_without_inserters(
            [schema_migration],
            [schema_migration],
        )

        assert len(result) == 1

    def test_removes_inserters(
        self,
        schema_migration: FakeMigration,
        inserter_migration: FakeMigration,
    ) -> None:
        """Protects against inserter migrations surviving the filter."""
        all_pending = [schema_migration, inserter_migration]

        result = MigrationPlanner.filter_without_inserters(all_pending, all_pending)

        assert len(result) == 1
        assert result[0].id == schema_migration.id

    def test_all_inserters_removed(self, migrations_root: Path) -> None:
        """Protects against non-empty result when all migrations are inserters."""
        ins1 = FakeMigration(
            id="seed_a",
            path=str(migrations_root / "billing" / "plans" / "inserters" / "seed_a.py"),
        )
        ins2 = FakeMigration(
            id="seed_b",
            path=str(migrations_root / "billing" / "plans" / "inserters" / "seed_b.py"),
        )

        result = MigrationPlanner.filter_without_inserters([ins1, ins2], [ins1, ins2])

        assert result == []

    def test_no_conflict_when_dep_is_schema(self, migrations_root: Path) -> None:
        """Protects against false conflict when a schema depends on another schema."""
        s1 = FakeMigration(
            id="create_table",
            path=str(migrations_root / "auth" / "users" / "create_table.py"),
        )
        s2 = FakeMigration(
            id="add_column",
            path=str(migrations_root / "auth" / "users" / "add_column.py"),
            depends={"create_table"},
        )

        result = MigrationPlanner.filter_without_inserters([s1, s2], [s1, s2])

        assert len(result) == 2
