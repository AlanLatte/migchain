"""YoyoBackendAdapter -- migration operations.

- pending() returns list
- applied() returns list
- acquire_lock() context manager works
- apply then rollback cycle
- pending count decreases after apply
"""

from pathlib import Path

import pytest

from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter


@pytest.mark.integration
class TestMigrationOperations:
    """Protects pending/applied/apply/rollback lifecycle against yoyo changes."""

    def test_pending_returns_list(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against pending() returning non-list type."""
        discovery = YoyoDiscoveryAdapter()
        dirs = discovery.discover_directories(examples_root)
        migrations = discovery.read_migrations(dirs)

        backend = YoyoBackendAdapter()
        backend.connect(postgres_dsn)

        pending = backend.pending(migrations)

        assert isinstance(pending, list)

    def test_applied_returns_list(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against applied() returning non-list type."""
        discovery = YoyoDiscoveryAdapter()
        dirs = discovery.discover_directories(examples_root)
        migrations = discovery.read_migrations(dirs)

        backend = YoyoBackendAdapter()
        backend.connect(postgres_dsn)

        applied = backend.applied(migrations)

        assert isinstance(applied, list)

    def test_acquire_lock(self, postgres_dsn: str):
        """Protects against acquire_lock context manager protocol breakage."""
        backend = YoyoBackendAdapter()
        backend.connect(postgres_dsn)

        with backend.acquire_lock():
            pass

    def test_apply_and_rollback(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against apply/rollback cycle failing on real migrations."""
        discovery = YoyoDiscoveryAdapter()
        dirs = discovery.discover_directories(
            examples_root,
            include_domains={"analytics"},
        )
        migrations = discovery.read_migrations(dirs)

        backend = YoyoBackendAdapter()
        backend.connect(postgres_dsn)

        applied_before = backend.applied(migrations)
        if applied_before:
            backend.rollback_one(applied_before[0])

        pending = backend.pending(migrations)
        if not pending:
            return

        first = pending[0]
        backend.apply_one(first)

        applied_after = backend.applied(migrations)
        applied_ids = [m.id for m in applied_after]
        assert first.id in applied_ids

        backend.rollback_one(first)

    def test_pending_decreases_after_apply(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against apply not affecting pending count."""
        discovery = YoyoDiscoveryAdapter()
        dirs = discovery.discover_directories(
            examples_root,
            include_domains={"analytics"},
        )
        migrations = discovery.read_migrations(dirs)

        backend = YoyoBackendAdapter()
        backend.connect(postgres_dsn)

        applied_existing = backend.applied(migrations)
        for m in applied_existing:
            backend.rollback_one(m)

        pending_before = backend.pending(migrations)
        if not pending_before:
            return

        backend.apply_one(pending_before[0])

        pending_after = backend.pending(migrations)
        assert len(pending_after) < len(pending_before)

        backend.rollback_one(pending_before[0])
