"""MigrationService -- apply edge cases.

- nothing pending -> no apply calls
- no_inserters mode -> skips inserter migrations
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestNothingPendingAndNoInserters:
    """Protects edge cases where apply has nothing to do or must filter inserters."""

    def test_nothing_pending(self, default_config: MigrationConfig):
        """Protects against backend calls when there are
        no pending migrations."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        backend.set_pending([])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("apply")

        assert len(backend.apply_calls) == 0

    def test_no_inserters_mode(self, default_config: MigrationConfig):
        """Protects against inserter migrations running
        when run_inserters=False."""
        default_config.run_inserters = False
        schema_mig = FakeMigration(
            id="schema_001",
            path=str(
                default_config.migrations_root / "domain" / "schema" / "001.py",
            ),
        )
        inserter_mig = FakeMigration(
            id="ins_001",
            path=str(
                default_config.migrations_root / "domain" / "inserters" / "001.py",
            ),
        )
        repo = FakeRepository(migrations=[schema_mig, inserter_mig])
        backend = FakeBackend()
        backend.set_pending([schema_mig, inserter_mig])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("apply")

        applied_ids = [m.id for m in backend.apply_calls]
        assert "schema_001" in applied_ids
        assert "ins_001" not in applied_ids
