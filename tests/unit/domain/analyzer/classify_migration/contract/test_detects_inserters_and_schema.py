"""MigrationAnalyzer.is_inserter_migration + get_migration_category -- classification.

- schema migration -> is_inserter=False, category="schema"
- inserter migration -> is_inserter=True, category="inserter"
"""

from migchain.domain.analyzer import MigrationAnalyzer
from tests.conftest import FakeMigration


class TestDetectsInsertersAndSchema:
    """Protects the classification contract: inserters
    directory triggers inserter category."""

    def test_schema_not_inserter(self, schema_migration: FakeMigration) -> None:
        """Protects against false positive inserter detection for schema migrations."""
        result = MigrationAnalyzer.is_inserter_migration(schema_migration)

        assert result is False

    def test_inserter_detected(self, inserter_migration: FakeMigration) -> None:
        """Protects against inserter migrations being misclassified as schema."""
        result = MigrationAnalyzer.is_inserter_migration(inserter_migration)

        assert result is True

    def test_schema_category(self, schema_migration: FakeMigration) -> None:
        """Protects against wrong category string for schema migrations."""
        result = MigrationAnalyzer.get_migration_category(schema_migration)

        assert result == "schema"

    def test_inserter_category(self, inserter_migration: FakeMigration) -> None:
        """Protects against wrong category string for inserter migrations."""
        result = MigrationAnalyzer.get_migration_category(inserter_migration)

        assert result == "inserter"
