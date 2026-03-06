"""MigrationService -- rollback one selects leaf.

- picks leaf migration (B when A->B)
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestRollbacksLeaf:
    """Protects the rollback-one leaf selection: always rolls back the leaf node."""

    def test_picks_leaf(self, default_config: MigrationConfig):
        """Protects against rolling back a parent migration when a leaf exists."""
        mig_a = FakeMigration(id="A", path=str(default_config.migrations_root / "a.py"))
        mig_b = FakeMigration(
            id="B",
            path=str(default_config.migrations_root / "b.py"),
            depends={"A"},
        )
        repo = FakeRepository(migrations=[mig_a, mig_b])
        backend = FakeBackend()
        backend.set_applied([mig_a, mig_b])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("rollback-one")

        assert len(backend.rollback_calls) == 1
        assert backend.rollback_calls[0].id == "B"
