"""FilesystemMigrationWriter.apply_to_source -- missing file.

- migration ID with no path -> skipped
- migration ID with nonexistent path -> skipped
"""

from migchain.infrastructure.migration_writer import FilesystemMigrationWriter


class TestMissingFile:
    """Protects against crashes when migration files are missing."""

    def test_none_path_skipped(self):
        """Protects against crash when migration has no path mapping."""
        writer = FilesystemMigrationWriter()
        modified = writer.apply_to_source(
            {},
            {"UNKNOWN": {"A"}},
        )
        assert not modified

    def test_nonexistent_path_skipped(self, tmp_path):
        """Protects against crash when migration file was deleted."""
        writer = FilesystemMigrationWriter()
        modified = writer.apply_to_source(
            {"M": tmp_path / "gone.py"},
            {"M": {"A"}},
        )
        assert not modified
