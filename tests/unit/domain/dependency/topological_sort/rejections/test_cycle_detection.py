"""DependencyResolver.topological_sort -- cycle detection.

- two-node cycle A<->B -> SystemExit
- self-cycle A->A -> SystemExit
- three-node cycle A->B->C->A -> SystemExit
"""

import pytest

from migchain.domain.dependency import DependencyResolver


class TestCycleDetection:
    """Protects the invariant: circular dependencies are detected and rejected."""

    def test_two_node_cycle(self) -> None:
        """Protects against mutual dependency going undetected."""
        deps = {"A": {"B"}, "B": {"A"}}

        with pytest.raises(SystemExit, match="Cycle detected"):
            DependencyResolver.topological_sort(deps)

    def test_self_cycle(self) -> None:
        """Protects against a migration depending on itself passing validation."""
        deps = {"A": {"A"}}

        with pytest.raises(SystemExit, match="Cycle detected"):
            DependencyResolver.topological_sort(deps)

    def test_three_node_cycle(self) -> None:
        """Protects against longer cycles evading Kahn's algorithm detection."""
        deps = {"A": {"C"}, "B": {"A"}, "C": {"B"}}

        with pytest.raises(SystemExit, match="Cycle detected"):
            DependencyResolver.topological_sort(deps)
