"""YoyoDiscoveryAdapter.discover_directories -- boundary conditions.

- empty directory -> empty list
- directory with only __init__.py -> empty list
"""

from pathlib import Path

import pytest

from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestEmptyAndInitOnly:
    """Protects against false positives from empty or init-only directories."""

    def test_empty_directory(self, tmp_path: Path):
        """Protects against empty dirs being reported as migration sources."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(tmp_path)

        assert dirs == []

    def test_ignores_init_files(self, tmp_path: Path):
        """Protects against __init__.py being counted as a migration file."""
        domain_dir = tmp_path / "domain"
        domain_dir.mkdir()
        (domain_dir / "__init__.py").write_text("")

        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(tmp_path)

        assert dirs == []
