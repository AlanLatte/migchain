"""MigrationService -- rollback latest batch.

- rolls back all migrations in latest batch
- records rollback in batch storage
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


class TestRollbacksBatch:
    """Protects the rollback-latest contract: undo the entire last batch."""

    def test_rollbacks_batch(self, default_config: MigrationConfig):
        """Protects against partial batch rollback or missing storage record."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        batch = FakeBatchStorage()
        batch.set_latest(1, ["A"])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("rollback-latest")

        assert len(backend.rollback_calls) == 1
        assert len(batch.record_rollback_calls) == 1
