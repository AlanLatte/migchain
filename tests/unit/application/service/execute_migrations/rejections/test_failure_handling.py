"""MigrationService -- migration failure handling.

- exception during apply -> on_migration_fail called, SystemExit raised
"""

import pytest

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class _FailingBackend(FakeBackend):
    """Backend that raises on first apply_one call."""

    def apply_one(self, migration):
        raise RuntimeError("DB connection lost")


class TestFailureHandling:
    """Protects error reporting when a migration fails mid-execution."""

    def test_calls_on_fail(self, default_config: MigrationConfig):
        """Protects against silent failure without on_migration_fail callback."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = _FailingBackend()
        backend.set_pending([migration])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )

        with pytest.raises(SystemExit):
            svc.run("apply")

        assert len(presenter.migration_fails) == 1
