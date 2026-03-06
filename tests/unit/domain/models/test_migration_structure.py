"""MigrationStructure — aggregate analysis result.

- all defaults are empty/zero
- stores domain stats correctly
"""

from migchain.domain.models import DomainStats, MigrationStructure


class TestDefaultsAreEmpty:
    """Protects the zero/empty default contract for all fields."""

    def test_defaults_are_empty(self) -> None:
        """Protects against non-zero or non-empty defaults on a fresh instance."""
        structure = MigrationStructure()

        assert structure.total == 0
        assert structure.schema_count == 0
        assert structure.inserter_count == 0
        assert structure.domains == {}
        assert structure.schema_paths == set()
        assert structure.inserter_paths == set()


class TestStoresDomainStats:
    """Protects that DomainStats integrates correctly into the domains dict."""

    def test_stores_domain_stats(self) -> None:
        """Protects against broken aggregation when DomainStats
        is stored inside MigrationStructure."""
        stats = DomainStats(schema_count=2, inserter_count=1)
        structure = MigrationStructure(domains={"users": stats})

        assert structure.domains["users"].total == 3
        assert structure.domains["users"].schema_count == 2
        assert structure.domains["users"].inserter_count == 1
