"""MigrationService._scaffold -- оркестрация создания новой миграции.

- operation_mode='new' вызывает _scaffold и возвращает
- presenter.prompt_scaffold получает домены и поддиректории
- presenter.info вызывается с путем созданного файла
"""

from migchain.application.config import MigrationConfig
from tests.unit.application.conftest import (
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestScaffoldFlow:
    """Защищает контракт оркестрации scaffolding через run('new')."""

    def test_scaffold_creates_migration_and_reports(self, tmp_path):
        """Защищает от потери вызова scaffolder при operation_mode='new'."""
        root = tmp_path / "migrations"
        root.mkdir()
        config = MigrationConfig(
            dsn="",
            migrations_root=root,
            auto_confirm=True,
        )
        presenter = FakePresenter()
        repo = FakeRepository()

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("new")

        assert any("Created" in msg for msg in presenter.infos)

    def test_scaffold_does_not_discover_migrations(self, tmp_path):
        """Защищает от ненужного вызова discover при scaffolding."""
        root = tmp_path / "migrations"
        root.mkdir()
        config = MigrationConfig(
            dsn="",
            migrations_root=root,
            auto_confirm=True,
        )
        repo = FakeRepository()
        presenter = FakePresenter()

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("new")

        assert len(repo.discover_calls) == 0
