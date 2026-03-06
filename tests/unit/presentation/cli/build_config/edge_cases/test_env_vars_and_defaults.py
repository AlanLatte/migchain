"""build_config -- environment variables and default behavior.

- DATABASE_URL env var used when --dsn not provided
- dry-run allows empty DSN
- --quiet sets verbosity to zero
"""

from migchain.presentation.cli import build_config


class TestEnvVarsAndDefaults:
    """Protects the contract of environment variable fallback and default behavior."""

    def test_dsn_from_env(self, base_namespace, tmp_path, monkeypatch):
        """Protects against DATABASE_URL env var not being used as DSN fallback."""
        base_namespace.dsn = None
        base_namespace.migrations_dir = str(tmp_path)
        monkeypatch.setenv("DATABASE_URL", "postgresql://env@localhost/envdb")
        config = build_config(base_namespace)
        assert config.dsn == "postgresql://env@localhost/envdb"

    def test_no_dsn_allowed_in_dry_run(self, base_namespace, tmp_path, monkeypatch):
        """Protects against dry-run mode requiring a DSN when none is available."""
        base_namespace.dry_run = True
        base_namespace.dsn = None
        base_namespace.migrations_dir = str(tmp_path)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        config = build_config(base_namespace)
        assert config.dsn == ""

    def test_quiet_sets_verbosity_zero(self, base_namespace, tmp_path):
        """Protects against --quiet not disabling verbose output in config."""
        base_namespace.quiet = True
        base_namespace.migrations_dir = str(tmp_path)
        config = build_config(base_namespace)
        assert config.verbose is False
