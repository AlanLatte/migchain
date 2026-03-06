"""MigrationService.run -- KeyboardInterrupt handling.

- KeyboardInterrupt during execution -> warning + SystemExit(1)
"""

from unittest.mock import patch

import pytest

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestKeyboardInterrupt:
    """Protects the graceful shutdown path when user presses Ctrl+C."""

    def test_keyboard_interrupt_raises_system_exit(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against unhandled KeyboardInterrupt propagating to caller."""
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

        with patch.object(
            backend,
            "apply_one",
            side_effect=KeyboardInterrupt,
        ):
            with pytest.raises(SystemExit) as exc_info:
                svc.run("apply")

        assert exc_info.value.code == 1
        assert any("interrupted" in msg.lower() for msg in presenter.warnings)
