"""MigrationService -- dry run mode.

- shows plan without backend calls
- exports JSON when configured
"""

import json

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakeBackend,
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestShowsPlanWithoutExecution:
    """Protects the dry-run contract: plan visibility without side effects."""

    def test_no_backend_calls(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against dry run accidentally
        executing migrations."""
        default_config.dry_run = True
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        backend = FakeBackend()
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            backend=backend,
            presenter=presenter,
        )
        svc.run("apply")

        assert len(backend.apply_calls) == 0
        assert len(backend.rollback_calls) == 0

    def test_shows_plan(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against dry run not displaying
        the migration plan."""
        default_config.dry_run = True
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            presenter=presenter,
        )
        svc.run("apply")

        assert len(presenter.plan_calls) >= 1

    def test_json_export(
        self,
        default_config: MigrationConfig,
        tmp_path,
    ):
        """Protects against JSON export producing invalid
        or missing output."""
        default_config.dry_run = True
        json_file = tmp_path / "plan.json"
        default_config.json_plan_output_file = str(json_file)
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        svc = make_service(
            default_config,
            repository=repo,
            presenter=presenter,
        )
        svc.run("apply")

        assert json_file.exists()
        data = json.loads(json_file.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert data[0]["id"] == "A"
