"""DependencyResolver.build_graph -- empty input.

- empty list -> empty dicts
"""

from collections import defaultdict

from migchain.domain.dependency import DependencyResolver


class TestEmptyGraph:
    """Protects boundary behavior: empty migration list
    produces empty graph structures."""

    def test_empty_migrations(self) -> None:
        """Protects against crash or non-empty result
        when no migrations are provided."""
        deps, reverse = DependencyResolver.build_graph([])

        assert deps == {}
        assert isinstance(reverse, defaultdict)
        assert len(reverse) == 0
