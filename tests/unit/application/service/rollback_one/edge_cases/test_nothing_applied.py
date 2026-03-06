"""MigrationService -- rollback one with nothing applied.

- logs "Nothing to rollback"
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestNothingApplied:
    """Protects user feedback when rollback-one has nothing to operate on."""

    def test_logs_info(self, default_config: MigrationConfig):
        """Protects against silent exit when no migrations are applied."""
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
        svc.run("rollback-one")

        assert any("nothing" in msg.lower() for msg in presenter.infos)
