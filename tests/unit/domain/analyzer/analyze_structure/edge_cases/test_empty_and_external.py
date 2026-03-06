"""MigrationAnalyzer.analyze_structure -- boundary inputs.

- empty list -> total=0, domains={}
- external migration -> domain="external"
"""

from pathlib import Path

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestEmptyAndExternal:
    """Protects the fallback behavior for empty input and out-of-root migrations."""

    def test_empty_migrations(self, migrations_root: Path) -> None:
        """Protects against crash or non-zero defaults on empty migration list."""
        result = MigrationAnalyzer.analyze_structure([], migrations_root)

        assert result.total == 0
        assert result.domains == {}

    def test_external_migration_domain(self, migrations_root: Path) -> None:
        """Protects against unhandled ValueError when migration is outside root."""
        migration = FakeMigration(id="ext", path="/other/place/ext.py")

        result = MigrationAnalyzer.analyze_structure([migration], migrations_root)

        assert "external" in result.domains
