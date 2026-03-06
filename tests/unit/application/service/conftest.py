"""Service-level test fixtures -- make_service helper."""

from migchain.application.config import MigrationConfig
from migchain.application.service import MigrationService
from tests.unit.application.conftest import (
    FakeBackend,
    FakeBatchStorage,
    FakePresenter,
    FakeRepository,
)


def make_service(
    config: MigrationConfig,
    repository: FakeRepository | None = None,
    backend: FakeBackend | None = None,
    batch_storage: FakeBatchStorage | None = None,
    presenter: FakePresenter | None = None,
) -> MigrationService:
    """Build a MigrationService wired to fake adapters."""
    return MigrationService(
        config=config,
        repository=repository or FakeRepository(),
        backend=backend or FakeBackend(),
        batch_storage=batch_storage or FakeBatchStorage(),
        presenter=presenter or FakePresenter(),
    )
