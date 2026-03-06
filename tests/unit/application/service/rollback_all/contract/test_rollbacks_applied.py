"""MigrationService -- rollback all contract.

- rolls back all applied migrations
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestRollbacksApplied:
    """Protects the rollback-all contract: every applied migration gets rolled back."""

    def test_rollbacks_applied(self, default_config: MigrationConfig):
        """Protects against applied migrations being skipped during rollback."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        backend.set_applied([migration])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("rollback")

        assert len(backend.rollback_calls) == 1
