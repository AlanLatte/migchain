"""TestcontainerSchemaComparator.verify -- identical schemas are safe.

- original and optimized migrations produce identical schemas
- verify returns is_safe=True with no differences
"""

from pathlib import Path

import pytest

from migchain.infrastructure.schema_comparator import TestcontainerSchemaComparator
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestIdenticalSchemas:
    """Protects the contract: same SQL produces identical snapshots."""

    def test_same_migrations_are_identical(self, redundant_migrations: Path):
        """Protects against false negatives when schemas are identical."""
        discovery = YoyoDiscoveryAdapter()
        paths = discovery.discover_directories(redundant_migrations)

        comparator = TestcontainerSchemaComparator()
        result = comparator.verify(paths, paths)

        assert result.is_safe is True
        assert result.differences == []
        assert result.original_snapshot is not None
        assert result.optimized_snapshot is not None

    def test_snapshot_captures_tables(self, redundant_migrations: Path):
        """Protects against empty schema snapshots."""
        discovery = YoyoDiscoveryAdapter()
        paths = discovery.discover_directories(redundant_migrations)

        comparator = TestcontainerSchemaComparator()
        result = comparator.verify(paths, paths)

        snapshot = result.original_snapshot
        assert len(snapshot.tables) > 0
        assert len(snapshot.indexes) > 0
