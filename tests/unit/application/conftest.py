"""Application layer test fixtures — fake adapters for all ports."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional, Sequence, Set, Tuple

import pytest

from migchain.application.config import MigrationConfig
from migchain.domain.models import (
    MigrationPlan,
    MigrationStructure,
    OptimizationResult,
    OptimizationVerification,
)


class FakeRepository:
    """Implements MigrationRepository port for testing."""

    def __init__(self, migrations=None):
        self._migrations = migrations or []
        self.discover_calls = []
        self.read_calls = []

    def discover_directories(
        self,
        root: Path,
        include_domains: Optional[Set[str]] = None,
        exclude_domains: Optional[Set[str]] = None,
        domain_level: int = 0,
    ) -> List[Path]:
        self.discover_calls.append(
            (root, include_domains, exclude_domains, domain_level),
        )
        if not self._migrations:
            return []
        return [root]

    def read_migrations(self, paths: Sequence[Path]) -> Any:
        self.read_calls.append(paths)
        return self._migrations


class FakeBackend:
    """Implements MigrationBackend port for testing."""

    def __init__(self):
        self._pending = []
        self._applied = []
        self._connection = object()
        self.connect_calls = []
        self.apply_calls = []
        self.rollback_calls = []
        self.connected = False

    @property
    def connection(self):
        return self._connection

    def connect(
        self,
        dsn: str,
        testing: bool = False,
        database_name_override: Optional[str] = None,
    ) -> None:
        self.connect_calls.append((dsn, testing, database_name_override))
        self.connected = True

    def set_pending(self, migrations):
        self._pending = list(migrations)

    def set_applied(self, migrations):
        self._applied = list(migrations)

    def pending(self, _migrations: Any) -> List[Any]:
        return self._pending

    def applied(self, _migrations: Any) -> List[Any]:
        return self._applied

    def apply_one(self, migration: Any) -> None:
        self.apply_calls.append(migration)

    def rollback_one(self, migration: Any) -> None:
        self.rollback_calls.append(migration)

    @contextmanager
    def acquire_lock(self):
        yield


class FakeBatchStorage:
    """Implements BatchStorage port for testing."""

    def __init__(self):
        self._batch_number = 1
        self._latest = None
        self.ensure_ready_calls = 0
        self.record_apply_calls = []
        self.record_rollback_calls = []

    def ensure_ready(self, _connection: Any) -> None:
        self.ensure_ready_calls += 1

    def next_batch_number(self, _connection: Any) -> int:
        return self._batch_number

    def set_batch_number(self, n: int) -> None:
        self._batch_number = n

    def set_latest(self, batch_number: int, ids: List[str]) -> None:
        self._latest = (batch_number, ids)

    def record_apply(
        self,
        _connection: Any,
        batch: int,
        ids: List[str],
    ) -> None:
        self.record_apply_calls.append((batch, ids))

    def record_rollback(
        self,
        _connection: Any,
        batch: int,
        ids: List[str],
    ) -> None:
        self.record_rollback_calls.append((batch, ids))

    def latest_batch(
        self,
        _connection: Any,
    ) -> Optional[Tuple[int, List[str]]]:
        return self._latest


class FakePresenter:
    """Implements Presenter port — records all calls for assertions."""

    def __init__(self):
        self.setup_calls = []
        self.structure_calls = []
        self.plan_calls = []
        self.graph_calls = []
        self.start_calls = []
        self.migration_starts = []
        self.migration_successes = []
        self.migration_fails = []
        self.finish_calls = 0
        self.confirm_result = True
        self.confirm_calls = []
        self.infos = []
        self.warnings = []
        self.errors = []
        self.debugs = []

    def setup(self, verbosity: int) -> None:
        self.setup_calls.append(verbosity)

    def show_structure(self, structure: MigrationStructure) -> None:
        self.structure_calls.append(structure)

    def show_plan(self, plan: MigrationPlan, mode: str) -> None:
        self.plan_calls.append((plan, mode))

    def show_graph(self, content: str) -> None:
        self.graph_calls.append(content)

    def start_execution(self, total: int, tag: str) -> None:
        self.start_calls.append((total, tag))

    def on_migration_start(self, migration_id: str, tag: str) -> None:
        self.migration_starts.append((migration_id, tag))

    def on_migration_success(
        self,
        migration_id: str,
        tag: str,
        duration: float,
    ) -> None:
        self.migration_successes.append((migration_id, tag, duration))

    def on_migration_fail(self, migration_id: str, tag: str) -> None:
        self.migration_fails.append((migration_id, tag))

    def finish_execution(self) -> None:
        self.finish_calls += 1

    def confirm(self, message: str) -> bool:
        self.confirm_calls.append(message)
        return self.confirm_result

    def info(self, message: str) -> None:
        self.infos.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def debug(self, message: str) -> None:
        self.debugs.append(message)

    def show_redundant_edges(self, result: OptimizationResult) -> None:
        self.infos.append(
            f"Redundant edges: {len(result.redundant_edges)}",
        )

    def show_verification_result(
        self,
        verification: OptimizationVerification,
    ) -> None:
        self.infos.append(
            f"Verification: safe={verification.is_safe}",
        )


@pytest.fixture
def default_config(tmp_path):
    root = tmp_path / "migrations"
    root.mkdir()
    return MigrationConfig(
        dsn="postgresql://user:pass@localhost:5432/testdb",
        migrations_root=root,
        auto_confirm=True,
    )


@pytest.fixture
def fake_repository():
    return FakeRepository()


@pytest.fixture
def fake_backend():
    return FakeBackend()


@pytest.fixture
def fake_batch_storage():
    return FakeBatchStorage()


@pytest.fixture
def fake_presenter():
    return FakePresenter()
