"""Full optimize cycle -- schema mismatch halts optimization.

- real migrations with broken optimized depends -> schema mismatch
- service raises SystemExit, files remain unchanged
"""

import pytest

from migchain.application.config import MigrationConfig
from migchain.application.service import MigrationService
from migchain.infrastructure.batch_tracker import PostgresBatchTracker
from migchain.infrastructure.migration_writer import FilesystemMigrationWriter
from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter
from migchain.presentation.plain import PlainPresenter
from tests.integration.optimizer.e2e.rejections.fake_unsafe_comparator import (
    FakeUnsafeComparator,
)


@pytest.mark.integration
class TestSchemaMismatchHalts:
    """Protects against applying changes when schema verification fails."""

    def test_unsafe_verification_raises(self, redundant_migrations):
        """Protects against file modification when schemas differ after optimization."""
        gamma_file = redundant_migrations / "test_domain" / "0004_create_gamma.py"
        original_content = gamma_file.read_text()

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
            schema_comparator=FakeUnsafeComparator(),
            migration_writer=FilesystemMigrationWriter(),
        )

        with pytest.raises(SystemExit, match="NOT safe"):
            service.run("optimize")

        assert gamma_file.read_text() == original_content
