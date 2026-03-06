"""GraphOptimizer.transitive_reduction -- edge cases.

- empty graph -> no redundancy
- single node -> no redundancy
- no edges at all -> zero counts
- independent nodes with no dependencies
"""

from migchain.domain.optimizer import GraphOptimizer


class TestEmptyAndSingle:
    """Protects against crashes on minimal graph inputs."""

    def test_empty_graph(self):
        """Protects against crash on empty dependency dict."""
        result = GraphOptimizer.transitive_reduction({})
        assert result.redundant_edges == []
        assert result.original_edge_count == 0
        assert result.reduced_edge_count == 0

    def test_single_node(self):
        """Protects against crash on a single node with no deps."""
        result = GraphOptimizer.transitive_reduction({"A": set()})
        assert result.redundant_edges == []
        assert result.original_edge_count == 0

    def test_independent_nodes(self):
        """Protects against false positives on disconnected nodes."""
        deps = {"A": set(), "B": set(), "C": set()}
        result = GraphOptimizer.transitive_reduction(deps)
        assert result.redundant_edges == []
        assert result.original_edge_count == 0
