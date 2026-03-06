"""DependencyResolver.extract_dependency_ids -- multi-format extraction.

- string set {"dep_a", "dep_b"} -> same set
- single string "dep_a" -> {"dep_a"}
- raw unmatched string -> used as-is
- object with .id -> {obj.id}
- list of strings -> set of all
- list of objects -> set of all ids
"""

from migchain.domain.dependency import DependencyResolver
from tests.conftest import FakeMigration


class TestExtractsFromVariousFormats:
    """Protects the contract: heterogeneous dependency formats
    are normalized to a set of IDs."""

    def test_from_string_set(self) -> None:
        """Protects against set-of-strings not being passed through correctly."""
        result = DependencyResolver.extract_dependency_ids({"dep_a", "dep_b"})

        assert result == {"dep_a", "dep_b"}

    def test_from_single_string(self) -> None:
        """Protects against single string not being wrapped into a set."""
        result = DependencyResolver.extract_dependency_ids("dep_a")

        assert result == {"dep_a"}

    def test_from_unmatched_string_uses_raw(self) -> None:
        """Protects against raw strings being silently dropped
        when they don't match the pattern."""
        result = DependencyResolver.extract_dependency_ids("raw_dep_id")

        assert result == {"raw_dep_id"}

    def test_from_object_with_id(self) -> None:
        """Protects against objects with .id attribute not being recognized."""
        obj = FakeMigration(id="dep_x")

        result = DependencyResolver.extract_dependency_ids(obj)

        assert result == {"dep_x"}

    def test_from_list_of_strings(self) -> None:
        """Protects against list iteration failing to collect all string elements."""
        result = DependencyResolver.extract_dependency_ids(["a", "b"])

        assert result == {"a", "b"}

    def test_from_list_of_objects(self) -> None:
        """Protects against list of objects not extracting .id from each element."""
        objs = [FakeMigration(id="x"), FakeMigration(id="y")]

        result = DependencyResolver.extract_dependency_ids(objs)

        assert result == {"x", "y"}
