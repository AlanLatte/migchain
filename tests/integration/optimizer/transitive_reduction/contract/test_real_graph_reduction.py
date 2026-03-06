"""GraphOptimizer + real yoyo migrations — transitive reduction on examples.

- detects known redundancy in example migrations
- preserves all necessary edges
"""

from pathlib import Path

import pytest

from migchain.domain.dependency import DependencyResolver
from migchain.domain.optimizer import GraphOptimizer
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestRealGraphReduction:
    """Protects transitive reduction against real migration dependency graphs."""

    def test_examples_have_redundancy(self, examples_root: Path):
        """Protects against false negatives on the known example redundancy."""
        if not examples_root.exists():
            pytest.skip("examples/migrations not found")

        discovery = YoyoDiscoveryAdapter()
        paths = discovery.discover_directories(examples_root)
        migrations = discovery.read_migrations(paths)

        deps, _ = DependencyResolver.build_graph(migrations)
        result = GraphOptimizer.transitive_reduction(deps)

        assert result.reduced_edge_count < result.original_edge_count
        assert len(result.redundant_edges) >= 1

        redundant_pairs = {(e.child_id, e.parent_id) for e in result.redundant_edges}
        assert (
            "20250104_01_create_user_events",
            "20250101_01_create_users",
        ) in redundant_pairs

    def test_synthetic_redundancy_detected(self, redundant_migrations: Path):
        """Protects against false negatives on synthetic test data."""
        discovery = YoyoDiscoveryAdapter()
        paths = discovery.discover_directories(redundant_migrations)
        migrations = discovery.read_migrations(paths)

        deps, _ = DependencyResolver.build_graph(migrations)
        result = GraphOptimizer.transitive_reduction(deps)

        assert len(result.redundant_edges) == 1
        edge = result.redundant_edges[0]
        assert edge.child_id == "0004_create_gamma"
        assert edge.parent_id == "0001_create_schema"

    def test_minimal_graph_no_reduction(self, minimal_migrations: Path):
        """Protects against false positives on minimal graphs."""
        discovery = YoyoDiscoveryAdapter()
        paths = discovery.discover_directories(minimal_migrations)
        migrations = discovery.read_migrations(paths)

        deps, _ = DependencyResolver.build_graph(migrations)
        result = GraphOptimizer.transitive_reduction(deps)

        assert result.redundant_edges == []
        assert result.original_edge_count == result.reduced_edge_count
