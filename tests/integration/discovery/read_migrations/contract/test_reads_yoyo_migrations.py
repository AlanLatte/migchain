"""YoyoDiscoveryAdapter.read_migrations -- yoyo migration loading.

- reads example migrations successfully
"""

from pathlib import Path

import pytest

from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestReadsYoyoMigrations:
    """Protects the read_migrations contract against yoyo API changes."""

    def test_reads_example_migrations(self, examples_root: Path):
        """Protects against yoyo failing to parse valid migration files."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(examples_root)
        migrations = adapter.read_migrations(dirs)

        assert len(migrations) > 0
