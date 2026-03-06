"""MigrationService._optimize -- full optimization flow.

- detects redundant edges and calls presenter
- prepares temp copies via writer
- delegates verification to schema comparator
- applies changes when verification passes
"""
# pylint: disable=protected-access

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

from migchain.application.config import MigrationConfig
from migchain.domain.models import OptimizationVerification, SchemaSnapshot
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class FakeSchemaComparator:
    """Fake SchemaComparator that returns configurable results."""

    def __init__(self, is_safe: bool = True):
        self._is_safe = is_safe
        self.verify_calls: List[tuple] = []

    def verify(
        self,
        original_paths: Sequence[Path],
        optimized_paths: Sequence[Path],
    ) -> OptimizationVerification:
        self.verify_calls.append((original_paths, optimized_paths))
        return OptimizationVerification(
            is_safe=self._is_safe,
            original_snapshot=SchemaSnapshot(),
            optimized_snapshot=SchemaSnapshot(),
        )


class FakeMigrationWriter:
    """Fake MigrationFileWriter that records calls."""

    def __init__(self, temp_root: Optional[Path] = None):
        self._temp_root = temp_root
        self.prepare_calls: List[tuple] = []
        self.apply_calls: List[tuple] = []

    def prepare_temp_copies(
        self,
        migrations_root: Path,
        optimized_dependencies: Dict[str, Set[str]],
        migration_id_to_path: Dict[str, Path],
    ) -> Path:
        self.prepare_calls.append(
            (migrations_root, optimized_dependencies, migration_id_to_path),
        )
        return self._temp_root or migrations_root

    def apply_to_source(
        self,
        migration_id_to_path: Dict[str, Path],
        optimized_dependencies: Dict[str, Set[str]],
    ) -> List[str]:
        self.apply_calls.append((migration_id_to_path, optimized_dependencies))
        return [str(p) for p in migration_id_to_path.values()]


class TestOptimizeFlow:
    """Protects the full optimization orchestration workflow."""

    def test_detects_and_applies_optimization(self, tmp_path):
        """Protects against optimization not applying changes when safe."""
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
        comparator = FakeSchemaComparator(is_safe=True)
        writer = FakeMigrationWriter(temp_root=root)

        config = MigrationConfig(
            migrations_root=root,
            auto_confirm=True,
        )

        svc = make_service(
            config,
            repository=repo,
            presenter=presenter,
        )
        svc._schema_comparator = comparator
        svc._migration_writer = writer

        svc.run("optimize")

        assert len(comparator.verify_calls) == 1
        assert len(writer.apply_calls) == 1
        assert any("complete" in m.lower() for m in presenter.infos)

    def test_no_redundancy_exits_early(self, tmp_path):
        """Protects against unnecessary verification when graph is already minimal."""
        root = tmp_path / "migrations"
        root.mkdir()

        m_a = FakeMigration(id="A", path=str(root / "a.py"))
        m_b = FakeMigration(id="B", path=str(root / "b.py"), depends={"A"})

        repo = FakeRepository(migrations=[m_a, m_b])
        presenter = FakePresenter()
        comparator = FakeSchemaComparator()
        writer = FakeMigrationWriter()

        config = MigrationConfig(
            migrations_root=root,
            auto_confirm=True,
        )

        svc = make_service(config, repository=repo, presenter=presenter)
        svc._schema_comparator = comparator
        svc._migration_writer = writer

        svc.run("optimize")

        assert len(comparator.verify_calls) == 0
        assert any("minimal" in m.lower() for m in presenter.infos)
