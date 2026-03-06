"""MigrationService -- rollback all with nothing applied.

- no applied migrations -> no rollback calls
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestEmptyApplied:
    """Protects against rollback attempting operations when nothing is applied."""

    def test_empty_applied(self, default_config: MigrationConfig):
        """Protects against backend calls when no migrations are applied."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        backend.set_applied([])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("rollback")

        assert len(backend.rollback_calls) == 0
