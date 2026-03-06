"""build_config -- validation constraints.

- no DSN and no env var -> SystemExit
- --gw-count without --testing -> SystemExit
- --gw-template without --gw-count -> SystemExit
- nonexistent migrations dir -> SystemExit
"""

import pytest

from migchain.presentation.cli import build_config


class TestValidationErrors:
    """Protects the contract of rejecting invalid argument combinations."""

    def test_no_dsn_no_env_raises(self, base_namespace, tmp_path, monkeypatch):
        """Protects against missing DSN being silently accepted without DATABASE_URL."""
        base_namespace.dsn = None
        base_namespace.migrations_dir = str(tmp_path)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        with pytest.raises(SystemExit, match="connection string required"):
            build_config(base_namespace)

    def test_gw_count_without_testing(self, base_namespace, tmp_path):
        """Protects against --gw-count being accepted without --testing flag."""
        base_namespace.migrations_dir = str(tmp_path)
        base_namespace.gw_count = 3
        base_namespace.testing = False
        with pytest.raises(SystemExit, match="requires --testing"):
            build_config(base_namespace)

    def test_gw_template_without_count(self, base_namespace, tmp_path):
        """Protects against --gw-template being accepted without --gw-count."""
        base_namespace.migrations_dir = str(tmp_path)
        base_namespace.gw_template = "test_{i}"
        base_namespace.gw_count = None
        with pytest.raises(SystemExit, match="requires --gw-count"):
            build_config(base_namespace)

    def test_nonexistent_dir(self, base_namespace):
        """Protects against nonexistent migrations directory being silently accepted."""
        base_namespace.migrations_dir = "/nonexistent/path"
        with pytest.raises(SystemExit, match="not found"):
            build_config(base_namespace)
