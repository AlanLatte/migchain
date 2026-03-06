"""YoyoDiscoveryAdapter.discover_directories -- filesystem walking.

- finds migration dirs under examples/migrations
- --include filter shows only matching domain
- --exclude filter hides matching domain
- output is sorted
- finds .py files in directory
- include+exclude combined
"""

from pathlib import Path

import pytest

from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestWalksFilesystem:
    """Protects the core directory-walking contract of discover_directories."""

    def test_discovers_example_migrations(self, examples_root: Path):
        """Protects against regression where valid migration dirs are missed."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(examples_root)

        assert len(dirs) > 0

    def test_include_filter(self, examples_root: Path):
        """Protects against include_domains filter being ignored."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(
            examples_root,
            include_domains={"auth"},
        )

        assert len(dirs) > 0
        for d in dirs:
            relative = d.relative_to(examples_root)
            assert "auth" in relative.parts

    def test_exclude_filter(self, examples_root: Path):
        """Protects against exclude_domains filter being ignored."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(
            examples_root,
            exclude_domains={"analytics"},
        )

        for d in dirs:
            relative = d.relative_to(examples_root)
            assert "analytics" not in relative.parts

    def test_sorted_output(self, examples_root: Path):
        """Protects against non-deterministic directory ordering."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(examples_root)

        assert dirs == sorted(dirs)

    def test_finds_py_files(self, tmp_path: Path):
        """Protects against .py files not being recognized as migrations."""
        domain_dir = tmp_path / "domain"
        domain_dir.mkdir()
        (domain_dir / "20250101.py").write_text("step = ''")

        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(tmp_path)

        assert domain_dir in dirs

    def test_include_and_exclude_combined(self, examples_root: Path):
        """Protects against incorrect precedence when both filters are active."""
        adapter = YoyoDiscoveryAdapter()

        dirs = adapter.discover_directories(
            examples_root,
            include_domains={"auth", "billing"},
            exclude_domains={"billing"},
        )

        assert len(dirs) > 0
        for d in dirs:
            relative = d.relative_to(examples_root)
            assert "auth" in relative.parts
            assert "billing" not in relative.parts
