"""MigrationService -- reload = rollback + apply.

- executes both rollback and apply phases
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestRunsBothPhases:
    """Protects the reload contract: rollback phase followed by apply phase."""

    def test_reload(self, default_config: MigrationConfig):
        """Protects against reload skipping either
        the rollback or apply phase."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        backend.set_applied([migration])
        backend.set_pending([migration])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("reload")

        assert len(backend.rollback_calls) >= 1
        assert len(backend.apply_calls) >= 1
