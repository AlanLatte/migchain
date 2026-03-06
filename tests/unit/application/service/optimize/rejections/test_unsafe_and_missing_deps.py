"""MigrationService._optimize -- rejection scenarios.

- schema mismatch -> reports error, does not apply
- missing schema_comparator -> raises SystemExit
"""
# pylint: disable=protected-access

from pathlib import Path
from typing import Dict, List, Sequence, Set

import pytest

from migchain.application.config import MigrationConfig
from migchain.domain.models import OptimizationVerification, SchemaSnapshot
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class FakeUnsafeComparator:
    """Fake comparator that always reports schema mismatch."""

    def verify(
        self,
        _original_paths: Sequence[Path],
        _optimized_paths: Sequence[Path],
    ) -> OptimizationVerification:
        return OptimizationVerification(
            is_safe=False,
            differences=["[tables] differs: users"],
            original_snapshot=SchemaSnapshot(),
            optimized_snapshot=SchemaSnapshot(),
        )


class FakeMigrationWriter:
    """Fake writer that returns migrations_root as temp_root."""

    def prepare_temp_copies(
        self,
        migrations_root: Path,
        _optimized_dependencies: Dict[str, Set[str]],
        _migration_id_to_path: Dict[str, Path],
    ) -> Path:
        return migrations_root

    def apply_to_source(
        self,
        _migration_id_to_path: Dict[str, Path],
        _optimized_dependencies: Dict[str, Set[str]],
    ) -> List[str]:
        return []


class TestUnsafeAndMissingDeps:
    """Protects against applying unsafe optimizations."""

    def test_unsafe_does_not_apply(self, tmp_path):
        """Protects against applying changes when schema comparison fails."""
        root = tmp_path / "migrations"
        root.mkdir()

        m_a = FakeMigration(id="A", path=str(root / "a.py"))
        m_b = FakeMigration(id="B", path=str(root / "b.py"), depends={"A"})
        m_c = FakeMigration(id="C", path=str(root / "c.py"), depends={"B"})
        m_d = FakeMigration(
            id="D",
            path=str(root / "d.py"),
            depends={"A", "C"},
        )

        repo = FakeRepository(migrations=[m_a, m_b, m_c, m_d])
        presenter = FakePresenter()

        config = MigrationConfig(migrations_root=root, auto_confirm=True)
        svc = make_service(config, repository=repo, presenter=presenter)
        svc._schema_comparator = FakeUnsafeComparator()
        svc._migration_writer = FakeMigrationWriter()

        with pytest.raises(SystemExit, match="NOT safe"):
            svc.run("optimize")

    def test_missing_comparator_raises(self, tmp_path):
        """Protects against running optimize without full deps."""
        root = tmp_path / "migrations"
        root.mkdir()

        m_a = FakeMigration(id="A", path=str(root / "a.py"))
        repo = FakeRepository(migrations=[m_a])
        presenter = FakePresenter()

        config = MigrationConfig(migrations_root=root, auto_confirm=True)
        svc = make_service(config, repository=repo, presenter=presenter)

        with pytest.raises(SystemExit):
            svc.run("optimize")
