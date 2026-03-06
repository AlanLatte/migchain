"""DomainStats — per-domain counters.

- total = schema_count + inserter_count
- defaults are zero
- migration_ids list is independent per instance
"""

from migchain.domain.models import DomainStats


class TestTotalSumsSchemaAndInserters:
    """Protects the total property contract: sum of schema and inserter counts."""

    def test_total_sums_schema_and_inserters(self) -> None:
        """Protects against broken arithmetic in total property."""
        stats = DomainStats(schema_count=3, inserter_count=2)

        assert stats.total == 5


class TestTotalZeroByDefault:
    """Protects the zero-default invariant for freshly created instances."""

    def test_total_zero_by_default(self) -> None:
        """Protects against non-zero defaults leaking into total."""
        stats = DomainStats()

        assert stats.total == 0


class TestMigrationIdsDefaultEmpty:
    """Protects the empty-list default for migration_ids."""

    def test_migration_ids_default_empty(self) -> None:
        """Protects against a non-empty default collection."""
        stats = DomainStats()

        assert stats.migration_ids == []


class TestMigrationIdsAreIndependentInstances:
    """Protects against shared mutable default between instances."""

    def test_migration_ids_are_independent_instances(self) -> None:
        """Protects against the mutable default argument pitfall in dataclasses."""
        stats_a = DomainStats()
        stats_b = DomainStats()

        stats_a.migration_ids.append("m001")

        assert stats_a.migration_ids == ["m001"]
        assert stats_b.migration_ids == []
