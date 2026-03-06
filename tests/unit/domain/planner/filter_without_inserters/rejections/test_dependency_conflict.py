"""MigrationPlanner.filter_without_inserters -- dependency conflict.

- schema depending on inserter -> SystemExit
"""

from pathlib import Path

import pytest

from migchain.domain.planner import MigrationPlanner
from tests.conftest import FakeMigration


class TestDependencyConflict:
    """Protects the safety invariant: schema migrations
    must not silently lose inserter dependencies."""

    def test_conflict_raises(
        self,
        migrations_root: Path,
    ) -> None:
        """Protects against silent data loss when a schema
        depends on a skipped inserter."""
        seed = FakeMigration(
            id="seed",
            path=str(migrations_root / "billing" / "plans" / "inserters" / "seed.py"),
        )
        schema = FakeMigration(
            id="add_fk",
            path=str(migrations_root / "auth" / "users" / "add_fk.py"),
            depends={"seed"},
        )

        with pytest.raises(SystemExit, match="depends on inserter"):
            MigrationPlanner.filter_without_inserters(
                [schema, seed],
                [schema, seed],
            )
