"""MigrationService -- apply operation contract.

- applies pending migrations via backend
- records batch via batch_storage
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


class TestAppliesPendingAndRecords:
    """Protects the core apply contract: execute pending and record batch."""

    def test_applies_pending(self, default_config: MigrationConfig):
        """Protects against pending migrations not being
        forwarded to backend."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        backend.set_pending([migration])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("apply")

        assert len(backend.apply_calls) == 1
        assert backend.apply_calls[0].id == "A"

    def test_records_batch(self, default_config: MigrationConfig):
        """Protects against applied migrations not being
        tracked in batch storage."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        backend.set_pending([migration])
        batch = FakeBatchStorage()
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("apply")

        assert batch.record_apply_calls == [(1, ["A"])]
