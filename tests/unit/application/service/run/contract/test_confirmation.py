"""MigrationService.run -- confirmation for destructive operations.

- rollback prompts confirmation
- cancelled operation logs info
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestConfirmation:
    """Protects the confirmation gate for destructive operations."""

    def test_rollback_prompts(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against destructive rollback bypassing
        user confirmation."""
        default_config.auto_confirm = False
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        presenter = FakePresenter()
        presenter.confirm_result = False

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("rollback")

        assert len(presenter.confirm_calls) == 1

    def test_cancelled_logs_info(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against silent cancellation without
        user feedback."""
        default_config.auto_confirm = False
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        presenter = FakePresenter()
        presenter.confirm_result = False

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("rollback")

        assert any("cancelled" in msg.lower() for msg in presenter.infos)
