"""MigrationService -- execution progress tracking.

- calls start_execution, on_migration_start, on_migration_success, finish_execution
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestProgressLifecycle:
    """Protects the full presenter lifecycle during migration execution."""

    def test_full_lifecycle(self, default_config: MigrationConfig):
        """Protects against missing lifecycle callbacks during execution."""
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

        assert len(presenter.start_calls) == 1
        assert len(presenter.migration_starts) == 1
        assert len(presenter.migration_successes) == 1
        assert presenter.finish_calls >= 1
