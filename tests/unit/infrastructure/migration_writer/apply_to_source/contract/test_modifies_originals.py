"""FilesystemMigrationWriter.apply_to_source -- modifies original files.

- rewrites __depends__ in actual migration files
- returns list of modified paths
- handles both set and list depends format
"""

from migchain.infrastructure.migration_writer import FilesystemMigrationWriter


class TestModifiesOriginals:
    """Protects the contract of applying optimization to source files."""

    def test_rewrites_set_depends(self, tmp_path):
        """Protects against set-style depends not being rewritten."""
        path = tmp_path / "migration.py"
        path.write_text('__depends__ = {"A", "B", "C"}\nsteps = []\n')

        writer = FilesystemMigrationWriter()
        modified = writer.apply_to_source(
            {"M": path},
            {"M": {"A"}},
        )

        assert len(modified) == 1
        content = path.read_text()
        assert '"A"' in content
        assert '"B"' not in content
        assert '"C"' not in content

    def test_rewrites_list_depends(self, tmp_path):
        """Protects against list-style depends not being rewritten."""
        path = tmp_path / "migration.py"
        path.write_text('depends = ["A", "B"]\nsteps = []\n')

        writer = FilesystemMigrationWriter()
        writer.apply_to_source({"M": path}, {"M": {"A"}})

        content = path.read_text()
        assert '"A"' in content
        assert '"B"' not in content
        assert "[" in content

    def test_returns_modified_paths(self, tmp_path):
        """Protects against missing paths in the return value."""
        p1 = tmp_path / "m1.py"
        p2 = tmp_path / "m2.py"
        p1.write_text('__depends__ = {"X"}\n')
        p2.write_text('__depends__ = {"Y"}\n')

        writer = FilesystemMigrationWriter()
        modified = writer.apply_to_source(
            {"M1": p1, "M2": p2},
            {"M1": {"X"}, "M2": set()},
        )

        assert len(modified) == 2
