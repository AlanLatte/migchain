"""MigrationPlan — execution plan counts from list lengths.

- counts match list lengths
- empty plan returns zeros
- all_migrations independent of categorized lists
"""

from migchain.domain.models import MigrationPlan
from tests.conftest import FakeMigration


class TestCountsMatchListLengths:
    """Protects that count properties reflect actual list sizes."""

    def test_counts_match_list_lengths(self) -> None:
        """Protects against count properties diverging from underlying list lengths."""
        schema = [FakeMigration(id="s1"), FakeMigration(id="s2")]
        inserters = [FakeMigration(id="i1")]
        all_migs = schema + inserters

        plan = MigrationPlan(
            schema_migrations=schema,
            inserter_migrations=inserters,
            all_migrations=all_migs,
        )

        assert plan.schema_count == 2
        assert plan.inserter_count == 1
        assert plan.total_count == 3


class TestEmptyPlanReturnsZeros:
    """Protects the zero-count invariant for an empty plan."""

    def test_empty_plan_returns_zeros(self) -> None:
        """Protects against non-zero counts when no migrations are provided."""
        plan = MigrationPlan()

        assert plan.schema_count == 0
        assert plan.inserter_count == 0
        assert plan.total_count == 0


class TestAllMigrationsIndependentOfCategorized:
    """Protects that all_migrations is a standalone list,
    not derived from schema + inserter."""

    def test_all_migrations_independent_of_categorized(
        self,
    ) -> None:
        """Protects against implicit coupling between
        all_migrations and categorized lists."""
        schema = [FakeMigration(id="s1")]
        inserters = [FakeMigration(id="i1")]
        extra = FakeMigration(id="x1")

        plan = MigrationPlan(
            schema_migrations=schema,
            inserter_migrations=inserters,
            all_migrations=[extra],
        )

        assert plan.schema_count == 1
        assert plan.inserter_count == 1
        assert plan.total_count == 1
        assert plan.all_migrations == [extra]
