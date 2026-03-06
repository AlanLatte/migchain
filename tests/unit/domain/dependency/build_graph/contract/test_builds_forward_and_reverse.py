"""DependencyResolver.build_graph -- graph construction.

- independent migrations -> empty dep sets
- linear chain A->B->C -> forward and reverse correct
- diamond A->B,C->D -> D depends on {B, C}
"""

from typing import List

from migchain.domain.dependency import DependencyResolver
from tests.conftest import FakeMigration


class TestBuildsForwardAndReverse:
    """Protects the contract: forward and reverse adjacency
    lists are built correctly."""

    def test_no_dependencies(self) -> None:
        """Protects against independent migrations getting spurious edges."""
        migrations = [
            FakeMigration(id="A"),
            FakeMigration(id="B"),
        ]

        deps, _ = DependencyResolver.build_graph(migrations)

        assert deps["A"] == set()
        assert deps["B"] == set()

    def test_linear_chain(self, linear_chain: List[FakeMigration]) -> None:
        """Protects against linear dependency chain being built incorrectly."""
        deps, _ = DependencyResolver.build_graph(linear_chain)

        assert deps["A"] == set()
        assert deps["B"] == {"A"}
        assert deps["C"] == {"B"}

    def test_diamond_dependencies(self, diamond_chain: List[FakeMigration]) -> None:
        """Protects against diamond pattern losing one of the two parent edges."""
        deps, _ = DependencyResolver.build_graph(diamond_chain)

        assert deps["D"] == {"B", "C"}

    def test_reverse_graph_populated(
        self,
        linear_chain: List[FakeMigration],
    ) -> None:
        """Protects against reverse adjacency list
        not being built from forward edges."""
        _, reverse = DependencyResolver.build_graph(linear_chain)

        assert "B" in reverse["A"]
        assert "C" in reverse["B"]
