"""DependencyResolver.extract_dependency_ids -- boundary inputs.

- None -> {"None"}
- empty set -> empty set
- nested list -> flattened
"""

from migchain.domain.dependency import DependencyResolver


class TestNoneAndEmpty:
    """Protects boundary behavior: None, empty collections, and nested structures."""

    def test_from_none(self) -> None:
        """Protects against None causing an exception instead of a string fallback."""
        result = DependencyResolver.extract_dependency_ids(None)

        assert result == {"None"}

    def test_from_empty_set(self) -> None:
        """Protects against empty set producing phantom dependencies."""
        result = DependencyResolver.extract_dependency_ids(set())

        assert result == set()

    def test_from_nested_list(self) -> None:
        """Protects against nested iterables not being recursively flattened."""
        result = DependencyResolver.extract_dependency_ids([["a"], "b"])

        assert result == {"a", "b"}
