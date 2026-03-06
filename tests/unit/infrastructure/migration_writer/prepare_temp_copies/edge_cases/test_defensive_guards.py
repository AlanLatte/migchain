"""FilesystemMigrationWriter.prepare_temp_copies -- defensive guards.

- existing temp dir is cleaned before copy
- unknown migration ID in optimized_dependencies is skipped
- path outside migrations_root is skipped (ValueError)
"""

from migchain.infrastructure.migration_writer import FilesystemMigrationWriter


class TestDefensiveGuards:
    """Protects against crashes on edge-case inputs during temp copy."""

    def test_existing_temp_dir_is_replaced(self, tmp_path):
        """Protects against stale temp dir contaminating new copies."""
        root = tmp_path / "migrations"
        root.mkdir()
        (root / "a.py").write_text(
            '__depends__ = {"X"}\nsteps = []\n',
        )

        stale_temp = root.parent / "_migchain_optimized"
        stale_temp.mkdir()
        (stale_temp / "stale_file.txt").write_text("old")

        writer = FilesystemMigrationWriter()
        temp = writer.prepare_temp_copies(
            root,
            {"A": {"X"}},
            {"A": root / "a.py"},
        )

        assert temp.exists()
        assert not (temp / "stale_file.txt").exists()
        assert (temp / "a.py").exists()

    def test_unknown_migration_id_skipped(self, tmp_path):
        """Protects against crash when optimized deps reference unknown migration."""
        root = tmp_path / "migrations"
        root.mkdir()
        (root / "a.py").write_text("steps = []\n")

        writer = FilesystemMigrationWriter()
        temp = writer.prepare_temp_copies(
            root,
            {"UNKNOWN": {"X"}},
            {},
        )

        assert temp.exists()

    def test_path_outside_root_skipped(self, tmp_path):
        """Protects against ValueError when migration path is outside root."""
        root = tmp_path / "migrations"
        root.mkdir()
        (root / "a.py").write_text("steps = []\n")

        outside = tmp_path / "elsewhere" / "m.py"
        outside.parent.mkdir(parents=True)
        outside.write_text('__depends__ = {"X"}\n')

        writer = FilesystemMigrationWriter()
        temp = writer.prepare_temp_copies(
            root,
            {"M": {"Y"}},
            {"M": outside},
        )

        assert temp.exists()
