"""DependencyResolver.build_graph -- missing dependency validation.

- migration depending on nonexistent ID -> SystemExit
"""

import pytest

from migchain.domain.dependency import DependencyResolver
from tests.conftest import FakeMigration


class TestMissingDependency:
    """Protects the invariant: every declared dependency
    must reference an existing migration."""

    def test_raises_on_missing(self) -> None:
        """Protects against silently ignoring references to nonexistent migrations."""
        migrations = [FakeMigration(id="A", depends={"nonexistent"})]

        with pytest.raises(SystemExit, match="Missing dependency"):
            DependencyResolver.build_graph(migrations)
