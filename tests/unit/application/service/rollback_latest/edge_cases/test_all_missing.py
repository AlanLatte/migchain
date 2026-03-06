"""MigrationService._rollback_latest -- all batch IDs missing.

- all migration IDs from batch not found in loaded migrations -> silent return
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakeBatchStorage,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestAllMissing:
    """Protects against crash when entire batch references deleted migrations."""

    def test_all_ids_missing_skips_rollback(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against executing rollback with an empty to_rollback list."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        batch = FakeBatchStorage()
        batch.set_latest(1, ["GONE_1", "GONE_2"])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("rollback-latest")

        assert len(presenter.warnings) == 2
        assert not backend.rollback_calls
