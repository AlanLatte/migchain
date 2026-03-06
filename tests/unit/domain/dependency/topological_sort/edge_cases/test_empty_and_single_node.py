"""DependencyResolver.topological_sort -- minimal graphs.

- empty graph -> empty list
- single node -> [node]
- independent nodes -> all present
"""

from migchain.domain.dependency import DependencyResolver


class TestEmptyAndSingleNode:
    """Protects boundary behavior: degenerate graphs produce valid, complete results."""

    def test_empty_graph(self) -> None:
        """Protects against crash or non-empty output on empty input."""
        result = DependencyResolver.topological_sort({})

        assert not result

    def test_single_node(self) -> None:
        """Protects against single-node graph being dropped or duplicated."""
        result = DependencyResolver.topological_sort({"A": set()})

        assert result == ["A"]

    def test_independent_nodes(self) -> None:
        """Protects against independent nodes being lost during sort."""
        deps = {"A": set(), "B": set(), "C": set()}

        result = DependencyResolver.topological_sort(deps)

        assert set(result) == {"A", "B", "C"}
        assert len(result) == 3
