"""YoyoDiscoveryAdapter.read_migrations -- empty paths.

- empty paths list -> SystemExit
"""

import pytest

from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestEmptyPaths:
    """Protects the fail-fast contract when no migration paths are provided."""

    def test_raises_on_empty(self):
        """Protects against silent no-op when caller passes empty paths."""
        adapter = YoyoDiscoveryAdapter()

        with pytest.raises(SystemExit, match="No migration folders"):
            adapter.read_migrations([])
