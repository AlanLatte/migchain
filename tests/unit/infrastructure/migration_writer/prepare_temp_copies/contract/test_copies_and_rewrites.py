"""FilesystemMigrationWriter.prepare_temp_copies -- copies and rewrites.

- creates temp directory with migration copies
- rewrites __depends__ in modified files
- preserves unmodified files intact
"""

from migchain.infrastructure.migration_writer import FilesystemMigrationWriter


class TestCopiesAndRewrites:
    """Protects the contract of creating optimized migration copies."""

    def test_creates_temp_copy(self, tmp_path):
        """Protects against temp directory not being created."""
        root = tmp_path / "migrations"
        root.mkdir()
        (root / "a.py").write_text(
            '__depends__ = {"X", "Y"}\nsteps = []\n',
        )

        writer = FilesystemMigrationWriter()
        temp = writer.prepare_temp_copies(
            root,
            {"A": {"X"}},
            {"A": root / "a.py"},
        )

        assert temp.exists()
        assert (temp / "a.py").exists()

    def test_rewrites_depends(self, tmp_path):
        """Protects against depends not being rewritten in temp copy."""
        root = tmp_path / "migrations"
        root.mkdir()
        (root / "a.py").write_text(
            '__depends__ = {"X", "Y"}\nsteps = []\n',
        )

        writer = FilesystemMigrationWriter()
        temp = writer.prepare_temp_copies(
            root,
            {"A": {"X"}},
            {"A": root / "a.py"},
        )

        content = (temp / "a.py").read_text()
        assert '"X"' in content
        assert '"Y"' not in content

    def test_preserves_unmodified_files(self, tmp_path):
        """Protects against unrelated files being corrupted."""
        root = tmp_path / "migrations"
        root.mkdir()
        (root / "a.py").write_text('__depends__ = {"X"}\nsteps = []\n')
        (root / "b.py").write_text("steps = []\n")

        writer = FilesystemMigrationWriter()
        temp = writer.prepare_temp_copies(
            root,
            {"A": {"X"}},
            {"A": root / "a.py"},
        )

        assert (temp / "b.py").read_text() == "steps = []\n"
