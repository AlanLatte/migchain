"""FilesystemMigrationWriter -- rewrite real yoyo migration files.

- rewrites __depends__ in set format
- preserves migration steps and docstring
- yoyo can still read the rewritten files
"""

import shutil
from pathlib import Path

import pytest

from migchain.infrastructure.migration_writer import FilesystemMigrationWriter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestRewriteRealMigrations:
    """Protects the contract of rewriting depends without breaking yoyo."""

    def test_rewritten_file_readable_by_yoyo(self, redundant_migrations: Path):
        """Protects against rewritten files being unreadable by yoyo."""
        gamma_file = redundant_migrations / "test_domain" / "0004_create_gamma.py"

        writer = FilesystemMigrationWriter()
        writer.apply_to_source(
            {"0004_create_gamma": gamma_file},
            {"0004_create_gamma": {"0003_create_beta"}},
        )

        discovery = YoyoDiscoveryAdapter()
        paths = discovery.discover_directories(redundant_migrations)
        migrations = discovery.read_migrations(paths)

        gamma = None
        for m in migrations:
            if m.id == "0004_create_gamma":
                gamma = m
                break

        assert gamma is not None
        dep_ids = {d.id if hasattr(d, "id") else str(d) for d in gamma.depends}
        assert "0003_create_beta" in dep_ids
        assert "0001_create_schema" not in dep_ids

    def test_preserves_steps(self, redundant_migrations: Path):
        """Protects against step content being corrupted during rewrite."""
        gamma_file = redundant_migrations / "test_domain" / "0004_create_gamma.py"
        original = gamma_file.read_text()
        assert "test_domain.gamma" in original

        writer = FilesystemMigrationWriter()
        writer.apply_to_source(
            {"0004_create_gamma": gamma_file},
            {"0004_create_gamma": {"0003_create_beta"}},
        )

        updated = gamma_file.read_text()
        assert "test_domain.gamma" in updated
        assert "step" in updated

    def test_temp_copies_preserve_structure(self, redundant_migrations: Path):
        """Protects against temp copy losing directory structure."""
        writer = FilesystemMigrationWriter()
        temp_root = writer.prepare_temp_copies(
            redundant_migrations,
            {"0004_create_gamma": {"0003_create_beta"}},
            {
                "0004_create_gamma": (
                    redundant_migrations / "test_domain" / "0004_create_gamma.py"
                ),
            },
        )

        assert (temp_root / "test_domain").is_dir()
        assert (temp_root / "test_domain" / "0004_create_gamma.py").exists()
        assert (temp_root / "test_domain" / "0001_create_schema.py").exists()

        shutil.rmtree(temp_root, ignore_errors=True)
