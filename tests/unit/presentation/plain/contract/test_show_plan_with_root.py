"""PlainPresenter.show_plan -- отображение плана с migrations_root.

- При передаче migrations_root извлекается домен миграции через MigrationAnalyzer
- Домен отображается в выводе вместо "unknown"
"""

import logging
from pathlib import Path
from unittest.mock import patch

from migchain.domain.models import MigrationPlan
from migchain.presentation.plain import PlainPresenter
from tests.conftest import FakeMigration


class TestShowPlanWithRoot:
    """Защищает извлечение домена при наличии migrations_root."""

    def test_extracts_domain_from_migration_path(self, caplog):
        """Защищает от игнорирования migrations_root при построении плана."""
        presenter = PlainPresenter()
        root = Path("/migrations")
        migration = FakeMigration(
            id="20250101_01_create_users",
            path="/migrations/auth/20250101_01_create_users.py",
        )
        plan = MigrationPlan(
            schema_migrations=[migration],
            all_migrations=[migration],
        )

        with patch(
            "migchain.presentation.plain.MigrationAnalyzer.get_migration_domain",
            return_value="auth",
        ) as mock_domain:
            with caplog.at_level(logging.INFO, logger="migchain"):
                presenter.show_plan(plan, "apply", migrations_root=root)

        mock_domain.assert_called_once_with(migration, root)
        assert "auth" in caplog.text
        assert "create_users" in caplog.text
