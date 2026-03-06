"""GraphOptimizer.transitive_reduction -- removes redundant edges.

- linear chain A->B->C: no redundancy
- diamond A->B, A->C, B->D, C->D, A->D: A->D is redundant
- multiple redundant edges detected simultaneously
- path information recorded for each redundant edge
"""

from migchain.domain.optimizer import GraphOptimizer


class TestRemovesRedundantEdges:
    """Protects the core transitive reduction contract."""

    def test_linear_chain_no_redundancy(self):
        """Protects against false positives in linear chains."""
        deps = {"A": set(), "B": {"A"}, "C": {"B"}}
        result = GraphOptimizer.transitive_reduction(deps)

        assert result.redundant_edges == []
        assert result.original_edge_count == 2
        assert result.reduced_edge_count == 2

    def test_diamond_with_shortcut(self):
        """Protects against missing the classic diamond shortcut."""
        deps = {
            "A": set(),
            "B": {"A"},
            "C": {"B"},
            "D": {"B", "C"},
        }
        result = GraphOptimizer.transitive_reduction(deps)

        assert len(result.redundant_edges) == 1
        edge = result.redundant_edges[0]
        assert edge.child_id == "D"
        assert edge.parent_id == "B"
        assert result.reduced_dependencies["D"] == {"C"}

    def test_multiple_redundant_edges(self):
        """Protects against stopping after the first redundant edge."""
        deps = {
            "A": set(),
            "B": {"A"},
            "C": {"B"},
            "D": {"A", "B", "C"},
        }
        result = GraphOptimizer.transitive_reduction(deps)

        redundant_pairs = {(e.child_id, e.parent_id) for e in result.redundant_edges}
        assert ("D", "A") in redundant_pairs
        assert ("D", "B") in redundant_pairs
        assert result.reduced_dependencies["D"] == {"C"}

    def test_path_recorded(self):
        """Protects against redundant edge path not being reported."""
        deps = {
            "A": set(),
            "B": {"A"},
            "C": {"A", "B"},
        }
        result = GraphOptimizer.transitive_reduction(deps)

        assert len(result.redundant_edges) == 1
        edge = result.redundant_edges[0]
        assert edge.child_id == "C"
        assert edge.parent_id == "A"
        assert len(edge.path) >= 2

    def test_edge_counts(self):
        """Protects against incorrect edge counting in result."""
        deps = {
            "A": set(),
            "B": {"A"},
            "C": {"B"},
            "D": {"A", "C"},
        }
        result = GraphOptimizer.transitive_reduction(deps)

        assert result.original_edge_count == 4
        assert result.reduced_edge_count == 3
