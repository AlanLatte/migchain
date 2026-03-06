"""MigrationAnalyzer.is_inserter_migration -- boundary inputs.

- empty path -> not inserter
- "inserters" in filename but not in path parts -> not inserter
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestEmptyAndFilenameTricks:
    """Protects against false positives from substring matching in path components."""

    def test_empty_path_not_inserter(self) -> None:
        """Protects against crash or false positive on empty path."""
        migration = FakeMigration(id="x", path="")

        result = MigrationAnalyzer.is_inserter_migration(migration)

        assert result is False

    def test_inserters_in_filename_not_detected(
        self,
        migrations_root: Path,
    ) -> None:
        """Protects against substring match treating filename
        as a directory component."""
        migration = FakeMigration(
            id="x",
            path=str(migrations_root / "auth" / "users" / "inserters_like.py"),
        )

        result = MigrationAnalyzer.is_inserter_migration(migration)

        assert result is False
