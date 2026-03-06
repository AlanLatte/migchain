"""MigrationService.run -- initialization and discovery.

- calls presenter.setup
- verbose config -> verbosity=2
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestSetupAndDiscovery:
    """Protects the initialization sequence of MigrationService.run."""

    def test_calls_presenter_setup(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against skipping presenter.setup
        during run."""
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

        assert len(presenter.setup_calls) == 1

    def test_verbose_sets_verbosity_2(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against verbose flag not propagating
        to presenter."""
        default_config.verbose = True
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

        assert presenter.setup_calls[0] == 2

    def test_apply_skips_confirmation(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against apply operation prompting
        for confirmation."""
        default_config.auto_confirm = False
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

        assert len(presenter.confirm_calls) == 0
