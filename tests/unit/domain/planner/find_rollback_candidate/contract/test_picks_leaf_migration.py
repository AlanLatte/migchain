"""MigrationPlanner.find_rollback_candidate -- leaf selection.

- single applied -> returns it
- linear chain all applied -> returns last (C)
- diamond all applied -> returns D (the leaf)
- partial applied A,B (C not applied) -> returns B
"""

from migchain.domain.planner import MigrationPlanner
from tests.conftest import FakeMigration


class TestPicksLeafMigration:
    """Protects the rollback contract: always picks a leaf node from the applied set."""

    def test_single_applied(self) -> None:
        """Protects against returning None when exactly one migration is applied."""
        a = FakeMigration(id="A")
        deps = {"A": set()}

        result = MigrationPlanner.find_rollback_candidate(
            applied=[a],
            dependencies=deps,
            all_migrations=[a],
        )

        assert result is not None
        assert result.id == "A"

    def test_linear_chain_picks_last(self) -> None:
        """Protects against picking a non-leaf node in a linear A->B->C chain."""
        a = FakeMigration(id="A")
        b = FakeMigration(id="B", depends={"A"})
        c = FakeMigration(id="C", depends={"B"})
        deps = {"A": set(), "B": {"A"}, "C": {"B"}}

        result = MigrationPlanner.find_rollback_candidate(
            applied=[a, b, c],
            dependencies=deps,
            all_migrations=[a, b, c],
        )

        assert result is not None
        assert result.id == "C"

    def test_diamond_picks_leaf(self) -> None:
        """Protects against selecting an intermediate node in a diamond graph."""
        a = FakeMigration(id="A")
        b = FakeMigration(id="B", depends={"A"})
        c = FakeMigration(id="C", depends={"A"})
        d = FakeMigration(id="D", depends={"B", "C"})
        deps = {"A": set(), "B": {"A"}, "C": {"A"}, "D": {"B", "C"}}

        result = MigrationPlanner.find_rollback_candidate(
            applied=[a, b, c, d],
            dependencies=deps,
            all_migrations=[a, b, c, d],
        )

        assert result is not None
        assert result.id == "D"

    def test_partial_applied(self) -> None:
        """Protects against returning an unapplied migration
        when only a subset is applied."""
        a = FakeMigration(id="A")
        b = FakeMigration(id="B", depends={"A"})
        c = FakeMigration(id="C", depends={"B"})
        deps = {"A": set(), "B": {"A"}, "C": {"B"}}

        result = MigrationPlanner.find_rollback_candidate(
            applied=[a, b],
            dependencies=deps,
            all_migrations=[a, b, c],
        )

        assert result is not None
        assert result.id == "B"
