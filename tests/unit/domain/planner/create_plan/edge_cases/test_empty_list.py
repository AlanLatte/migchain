"""MigrationPlanner.create_plan -- empty input.

- empty list -> all counts zero
"""

from migchain.domain.planner import MigrationPlanner


class TestEmptyList:
    """Protects against non-zero defaults when plan is created from empty input."""

    def test_empty_plan(self) -> None:
        """Protects against total_count being non-zero for an empty migration list."""
        plan = MigrationPlanner.create_plan([])

        assert plan.total_count == 0
        assert plan.schema_count == 0
        assert plan.inserter_count == 0
