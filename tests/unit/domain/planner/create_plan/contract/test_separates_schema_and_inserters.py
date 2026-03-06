"""MigrationPlanner.create_plan -- schema/inserter separation.

- schema-only list -> schema_count correct, inserter_count=0
- inserter-only list -> schema_count=0
- mixed list -> both counts correct
- all_migrations preserves original order
- schema_migrations filtered correctly
"""

from migchain.domain.planner import MigrationPlanner
from tests.conftest import FakeMigration


class TestSeparatesSchemaAndInserters:
    """Protects the plan creation contract: correct categorization and counting."""

    def test_schema_only(self, schema_migration: FakeMigration) -> None:
        """Protects against schema migrations being miscounted or misclassified."""
        plan = MigrationPlanner.create_plan([schema_migration])

        assert plan.schema_count == 1
        assert plan.inserter_count == 0

    def test_inserter_only(self, inserter_migration: FakeMigration) -> None:
        """Protects against inserter-only lists producing non-zero schema count."""
        plan = MigrationPlanner.create_plan([inserter_migration])

        assert plan.schema_count == 0
        assert plan.inserter_count == 1

    def test_mixed(
        self,
        schema_migration: FakeMigration,
        inserter_migration: FakeMigration,
    ) -> None:
        """Protects against incorrect totals when both types are present."""
        plan = MigrationPlanner.create_plan([schema_migration, inserter_migration])

        assert plan.schema_count == 1
        assert plan.inserter_count == 1
        assert plan.total_count == 2

    def test_preserves_order(
        self,
        schema_migration: FakeMigration,
        inserter_migration: FakeMigration,
    ) -> None:
        """Protects against all_migrations reordering the input list."""
        plan = MigrationPlanner.create_plan([schema_migration, inserter_migration])

        assert plan.all_migrations[0].id == schema_migration.id
        assert plan.all_migrations[1].id == inserter_migration.id

    def test_schema_list_filtered(
        self,
        schema_migration: FakeMigration,
        inserter_migration: FakeMigration,
    ) -> None:
        """Protects against inserters leaking into schema_migrations list."""
        plan = MigrationPlanner.create_plan([schema_migration, inserter_migration])

        assert len(plan.schema_migrations) == 1
        assert plan.schema_migrations[0].id == schema_migration.id
