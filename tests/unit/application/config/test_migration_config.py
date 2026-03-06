"""MigrationConfig -- configuration dataclass defaults.

- dsn defaults to empty string
- domain_level defaults to DEFAULT_DOMAIN_LEVEL
- boolean flags default to False
- optional fields default to None
"""

from pathlib import Path

from migchain.application.config import MigrationConfig
from migchain.constants import DEFAULT_DOMAIN_LEVEL


class TestMigrationConfig:
    """Protects the default contract of MigrationConfig dataclass."""

    def test_defaults(self):
        """Protects against regressions in default field values."""
        cfg = MigrationConfig()

        assert cfg.dsn == ""
        assert cfg.domain_level == DEFAULT_DOMAIN_LEVEL
        assert cfg.run_inserters is True
        assert cfg.dry_run is False
        assert cfg.testing is False
        assert cfg.verbose is False
        assert cfg.auto_confirm is False
        assert cfg.show_structure is False
        assert cfg.show_graph is False
        assert cfg.include_domains is None
        assert cfg.exclude_domains is None
        assert cfg.graph_output_file is None
        assert cfg.json_plan_output_file is None
        assert cfg.gw_count is None
        assert cfg.gw_template is None

    def test_custom_values(self, tmp_path: Path):
        """Protects against ignored constructor arguments."""
        root = tmp_path / "mig"
        root.mkdir()

        cfg = MigrationConfig(
            dsn="postgresql://u:p@h:5432/db",
            migrations_root=root,
            include_domains={"users", "billing"},
            dry_run=True,
        )

        assert cfg.dsn == "postgresql://u:p@h:5432/db"
        assert cfg.migrations_root == root
        assert cfg.include_domains == {"users", "billing"}
        assert cfg.dry_run is True

    def test_migrations_root_default_is_path(self):
        """Protects against migrations_root being a raw string instead of Path."""
        cfg = MigrationConfig()

        assert hasattr(cfg.migrations_root, "exists")
