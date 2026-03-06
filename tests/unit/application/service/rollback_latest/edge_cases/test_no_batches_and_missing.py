"""MigrationService -- rollback latest edge cases.

- no tracked batches -> logs info
- empty batch -> logs info about empty
- missing migration in batch -> logs warning
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakeBatchStorage,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestNoBatchesAndMissing:
    """Protects user feedback for degenerate rollback-latest scenarios."""

    def test_no_batches(self, default_config: MigrationConfig):
        """Protects against silent exit when no batches
        have been tracked."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        batch = FakeBatchStorage()
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("rollback-latest")

        assert any("no tracked" in msg.lower() for msg in presenter.infos)

    def test_empty_batch(self, default_config: MigrationConfig):
        """Protects against attempting rollback on an
        already-empty batch."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        batch = FakeBatchStorage()
        batch.set_latest(1, [])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("rollback-latest")

        assert any("empty" in msg.lower() for msg in presenter.infos)

    def test_missing_migration(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against crash when a batch references
        a deleted migration file."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        batch = FakeBatchStorage()
        batch.set_latest(1, ["A", "MISSING"])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("rollback-latest")

        assert any("not found" in msg.lower() for msg in presenter.warnings)
