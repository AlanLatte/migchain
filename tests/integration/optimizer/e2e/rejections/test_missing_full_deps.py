"""Full optimize cycle -- missing optional dependencies.

- schema_comparator=None -> SystemExit with install hint
- migration_writer=None -> SystemExit with install hint
"""

import pytest

from migchain.application.config import MigrationConfig
from migchain.application.service import MigrationService
from migchain.infrastructure.batch_tracker import PostgresBatchTracker
from migchain.infrastructure.schema_comparator import (
    TestcontainerSchemaComparator,
)
from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter
from migchain.presentation.plain import PlainPresenter


@pytest.mark.integration
class TestMissingFullDeps:
    """Protects against silent failure when [full] extras not installed."""

    def test_no_comparator_raises(self, redundant_migrations):
        """Protects against optimization proceeding without schema comparator."""
        config = MigrationConfig(
            migrations_root=redundant_migrations,
            auto_confirm=True,
        )

        service = MigrationService(
            config=config,
            repository=YoyoDiscoveryAdapter(),
            backend=YoyoBackendAdapter(),
            batch_storage=PostgresBatchTracker(),
            presenter=PlainPresenter(),
            schema_comparator=None,
            migration_writer=None,
        )

        with pytest.raises(SystemExit, match="migchain\\[full\\]"):
            service.run("optimize")

    def test_no_writer_raises(self, redundant_migrations):
        """Protects against optimization proceeding without migration writer."""
        config = MigrationConfig(
            migrations_root=redundant_migrations,
            auto_confirm=True,
        )

        service = MigrationService(
            config=config,
            repository=YoyoDiscoveryAdapter(),
            backend=YoyoBackendAdapter(),
            batch_storage=PostgresBatchTracker(),
            presenter=PlainPresenter(),
            schema_comparator=TestcontainerSchemaComparator(),
            migration_writer=None,
        )

        with pytest.raises(SystemExit, match="migchain\\[full\\]"):
            service.run("optimize")
