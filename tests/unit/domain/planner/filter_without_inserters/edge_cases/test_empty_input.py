"""MigrationPlanner.filter_without_inserters -- empty input.

- empty list -> empty result
"""

from migchain.domain.planner import MigrationPlanner


class TestEmptyInput:
    """Protects against non-empty result or crash when input lists are empty."""

    def test_empty_list(self) -> None:
        """Protects against returning non-empty list for empty input."""
        result = MigrationPlanner.filter_without_inserters([], [])

        assert result == []
