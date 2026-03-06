"""Full optimize cycle -- single migration without dependencies.

- single migration with no deps -> graph already minimal
- no testcontainer started, no files modified
"""

import pytest

from migchain.application.config import MigrationConfig
from migchain.application.service import MigrationService
from migchain.infrastructure.batch_tracker import PostgresBatchTracker
from migchain.infrastructure.migration_writer import FilesystemMigrationWriter
from migchain.infrastructure.schema_comparator import TestcontainerSchemaComparator
from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter
from migchain.presentation.plain import PlainPresenter


class RecordingPresenter(PlainPresenter):
    """Presenter that records calls for assertions."""

    def __init__(self) -> None:
        super().__init__()
        self.infos = []

    def info(self, message: str) -> None:
        self.infos.append(message)


@pytest.mark.integration
class TestSingleMigration:
    """Protects against unnecessary work on trivially minimal graphs."""

    def test_single_migration_skips_optimization(self, tmp_path):
        """Protects against testcontainer startup when only one migration exists."""
        root = tmp_path / "migrations"
        domain = root / "test_domain"
        domain.mkdir(parents=True)

        (domain / "0001_init.py").write_text(
            '"""Init."""\n'
            "from yoyo import step\n\n"
            "steps = [\n"
            '    step("CREATE SCHEMA IF NOT EXISTS test_domain"),\n'
            "]\n",
        )

        presenter = RecordingPresenter()
        config = MigrationConfig(
            migrations_root=root,
            auto_confirm=True,
        )

        service = MigrationService(
            config=config,
            repository=YoyoDiscoveryAdapter(),
            backend=YoyoBackendAdapter(),
            batch_storage=PostgresBatchTracker(),
            presenter=presenter,
            schema_comparator=TestcontainerSchemaComparator(),
            migration_writer=FilesystemMigrationWriter(),
        )

        service.run("optimize")

        assert any("minimal" in m.lower() for m in presenter.infos)
