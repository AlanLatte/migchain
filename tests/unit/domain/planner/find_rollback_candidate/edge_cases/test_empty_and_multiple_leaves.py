"""MigrationPlanner.find_rollback_candidate -- boundary conditions.

- empty applied -> None
- multiple leaves -> picks max ID
- no leaf (cycle-like deps) -> falls back to first
"""

from migchain.domain.planner import MigrationPlanner
from tests.conftest import FakeMigration


class TestEmptyAndMultipleLeaves:
    """Protects against crashes and wrong picks on degenerate dependency graphs."""

    def test_empty_returns_none(self) -> None:
        """Protects against returning a non-None value when nothing is applied."""
        result = MigrationPlanner.find_rollback_candidate(
            applied=[],
            dependencies={},
            all_migrations=[],
        )

        assert result is None

    def test_multiple_leaves_picks_max(self) -> None:
        """Protects against non-deterministic selection when two leaves exist."""
        a = FakeMigration(id="A")
        b = FakeMigration(id="B", depends={"A"})
        c = FakeMigration(id="C", depends={"A"})
        deps = {"A": set(), "B": {"A"}, "C": {"A"}}

        result = MigrationPlanner.find_rollback_candidate(
            applied=[a, b, c],
            dependencies=deps,
            all_migrations=[a, b, c],
        )

        assert result is not None
        assert result.id == "C"

    def test_no_leaf_falls_back_to_first(self) -> None:
        """Protects against crash when all applied nodes
        have applied children (cycle-like)."""
        a = FakeMigration(id="A", depends={"B"})
        b = FakeMigration(id="B", depends={"A"})
        deps = {"A": {"B"}, "B": {"A"}}

        result = MigrationPlanner.find_rollback_candidate(
            applied=[a, b],
            dependencies=deps,
            all_migrations=[a, b],
        )

        assert result is not None
        assert result.id == a.id
