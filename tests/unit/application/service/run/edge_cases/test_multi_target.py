"""MigrationService.run -- multi-target database logging.

- gw_count with testing -> logs per-database progress
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


class TestMultiTarget:
    """Protects per-database progress logging for gateway configurations."""

    def test_logs_database_index_for_each_target(self, tmp_path):
        """Protects against silent multi-database execution
        without progress feedback."""
        root = tmp_path / "migrations"
        root.mkdir()
        migration = FakeMigration(id="A", path=str(root / "a.py"))
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        batch = FakeBatchStorage()
        presenter = FakePresenter()

        config = MigrationConfig(
            dsn="postgresql://u:p@localhost:5432/mydb",
            migrations_root=root,
            auto_confirm=True,
            testing=True,
            gw_count=2,
        )

        svc = make_service(
            config,
            repository=repo,
            backend=backend,
            batch_storage=batch,
            presenter=presenter,
        )
        svc.run("apply")

        target_msgs = [m for m in presenter.infos if "Processing database" in m]
        assert len(target_msgs) == 3
