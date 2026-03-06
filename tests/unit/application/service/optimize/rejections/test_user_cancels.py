"""MigrationService._optimize -- user cancels via confirm.

- auto_confirm=False + presenter returns False -> cancelled
"""
# pylint: disable=protected-access

from pathlib import Path
from typing import Dict, List, Sequence, Set

from migchain.application.config import MigrationConfig
from migchain.domain.models import OptimizationVerification, SchemaSnapshot
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class FakeSafeComparator:
    """Fake comparator that always passes."""

    def verify(
        self,
        _original_paths: Sequence[Path],
        _optimized_paths: Sequence[Path],
    ) -> OptimizationVerification:
        return OptimizationVerification(
            is_safe=True,
            original_snapshot=SchemaSnapshot(),
            optimized_snapshot=SchemaSnapshot(),
        )


class FakeWriter:
    """Fake writer returning root as temp."""

    def __init__(self, root: Path):
        self._root = root
        self.apply_calls = 0

    def prepare_temp_copies(
        self,
        _migrations_root: Path,
        _optimized_dependencies: Dict[str, Set[str]],
        _migration_id_to_path: Dict[str, Path],
    ) -> Path:
        return self._root

    def apply_to_source(
        self,
        _migration_id_to_path: Dict[str, Path],
        _optimized_dependencies: Dict[str, Set[str]],
    ) -> List[str]:
        self.apply_calls += 1
        return []


class TestUserCancels:
    """Protects against applying changes when user declines."""

    def test_user_declines_cancels(self, tmp_path):
        """Protects against applying optimization when user says no."""
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
        presenter.confirm_result = False
        writer = FakeWriter(root)

        config = MigrationConfig(
            migrations_root=root,
            auto_confirm=False,
        )

        svc = make_service(config, repository=repo, presenter=presenter)
        svc._schema_comparator = FakeSafeComparator()
        svc._migration_writer = writer

        svc.run("optimize")

        assert writer.apply_calls == 0
        assert any("cancelled" in m.lower() for m in presenter.infos)
