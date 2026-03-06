"""build_config -- converts namespace to MigrationConfig.

- basic args -> correct dsn and migrations_root
- --include "auth, billing" -> parsed to set
- --exclude "analytics" -> parsed to set
- --no-inserters -> run_inserters=False
"""

from migchain.presentation.cli import build_config


class TestBuildsFromArgs:
    """Protects the contract of converting argparse namespace to MigrationConfig."""

    def test_basic_config(self, base_namespace, tmp_path):
        """Protects against basic namespace not producing
        correct dsn and migrations_root."""
        base_namespace.migrations_dir = str(tmp_path)
        config = build_config(base_namespace)
        assert config.dsn == "postgresql://user:pass@localhost:5432/testdb"
        assert config.migrations_root == tmp_path.resolve()

    def test_include_domains_parsed(
        self,
        base_namespace,
        tmp_path,
    ):
        """Protects against --include not being split into
        a set of stripped domain names."""
        base_namespace.migrations_dir = str(tmp_path)
        base_namespace.include = "auth, billing"
        config = build_config(base_namespace)
        assert config.include_domains == {"auth", "billing"}

    def test_exclude_domains_parsed(
        self,
        base_namespace,
        tmp_path,
    ):
        """Protects against --exclude not being split into
        a set of stripped domain names."""
        base_namespace.migrations_dir = str(tmp_path)
        base_namespace.exclude = "analytics"
        config = build_config(base_namespace)
        assert config.exclude_domains == {"analytics"}

    def test_no_inserters_flag(self, base_namespace, tmp_path):
        """Protects against --no-inserters not disabling run_inserters in config."""
        base_namespace.migrations_dir = str(tmp_path)
        base_namespace.no_inserters = True
        config = build_config(base_namespace)
        assert config.run_inserters is False
