"""Full optimization cycle — detect, verify, apply.

- detects redundant dependency in synthetic migrations
- verifies schema consistency via testcontainers
- applies changes to migration files
- resulting files have reduced depends
"""

from pathlib import Path

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
        self.warnings = []
        self.errors = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


@pytest.mark.integration
@pytest.mark.slow
class TestFullOptimizeCycle:
    """Protects the end-to-end optimization workflow with real PostgreSQL."""

    def test_detects_and_safely_removes_redundancy(
        self,
        redundant_migrations: Path,
    ):
        """Protects against optimization breaking database schema consistency."""
        gamma_file = redundant_migrations / "test_domain" / "0004_create_gamma.py"
        original_content = gamma_file.read_text()
        assert "0001_create_schema" in original_content
        assert "0003_create_beta" in original_content

        presenter = RecordingPresenter()

        config = MigrationConfig(
            migrations_root=redundant_migrations,
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

        updated_content = gamma_file.read_text()
        assert "0003_create_beta" in updated_content
        assert "0001_create_schema" not in updated_content

        assert any("complete" in m.lower() for m in presenter.infos)
        assert not presenter.errors

    def test_minimal_graph_skips_verification(
        self,
        minimal_migrations: Path,
    ):
        """Protects against unnecessary testcontainer startup for minimal graphs."""
        presenter = RecordingPresenter()

        config = MigrationConfig(
            migrations_root=minimal_migrations,
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
