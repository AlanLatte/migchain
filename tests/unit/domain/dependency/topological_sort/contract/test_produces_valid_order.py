"""DependencyResolver.topological_sort -- ordering guarantees.

- linear A->B->C -> A before B before C
- diamond -> correct partial order
- complex DAG with 5 nodes
"""

from migchain.domain.dependency import DependencyResolver


class TestProducesValidOrder:
    """Protects the contract: topological order respects all dependency edges."""

    def test_linear_order(self) -> None:
        """Protects against dependencies appearing after their dependents."""
        deps = {"A": set(), "B": {"A"}, "C": {"B"}}

        result = DependencyResolver.topological_sort(deps)

        assert result.index("A") < result.index("B") < result.index("C")

    def test_diamond_order(self) -> None:
        """Protects against diamond pattern violating partial order constraints."""
        deps = {"A": set(), "B": {"A"}, "C": {"A"}, "D": {"B", "C"}}

        result = DependencyResolver.topological_sort(deps)

        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("D")

    def test_complex_dag(self) -> None:
        """Protects against incorrect ordering in a five-node DAG
        with converging paths."""
        deps = {
            "A": set(),
            "B": {"A"},
            "C": {"A"},
            "D": {"B"},
            "E": {"C", "D"},
        }

        result = DependencyResolver.topological_sort(deps)

        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("E")
        assert result.index("D") < result.index("E")
