"""MigrationService._export_plan_json -- экспорт плана в JSON.

- dry_run + json_plan_output_file -> создает JSON файл
- JSON содержит id, path, domain, category, depends для каждой миграции
"""

import json

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestExportsPlan:
    """Защищает контракт экспорта плана миграций в JSON."""

    def test_json_contains_all_migration_fields(self, tmp_path):
        """Защищает от потери полей в JSON-экспорте плана миграций."""
        root = tmp_path / "migrations"
        root.mkdir()
        domain_dir = root / "users"
        domain_dir.mkdir()

        json_file = tmp_path / "plan.json"
        config = MigrationConfig(
            dsn="",
            migrations_root=root,
            auto_confirm=True,
            dry_run=True,
            json_plan_output_file=str(json_file),
        )

        migration = FakeMigration(
            id="20250101_01_create_users",
            path=str(domain_dir / "20250101_01_create_users.py"),
            depends=set(),
        )
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("apply")

        assert json_file.exists()
        data = json.loads(json_file.read_text(encoding="utf-8"))

        assert len(data) == 1
        entry = data[0]
        assert entry["id"] == "20250101_01_create_users"
        assert entry["domain"] == "users"
        assert entry["category"] == "schema"
        assert isinstance(entry["depends"], list)
        assert "path" in entry

    def test_json_export_with_dependencies(self, tmp_path):
        """Защищает от потери зависимостей в JSON-экспорте."""
        root = tmp_path / "migrations"
        root.mkdir()
        domain_dir = root / "orders"
        domain_dir.mkdir()

        json_file = tmp_path / "plan_deps.json"
        config = MigrationConfig(
            dsn="",
            migrations_root=root,
            auto_confirm=True,
            dry_run=True,
            json_plan_output_file=str(json_file),
        )

        m1 = FakeMigration(
            id="20250101_01_create_orders",
            path=str(domain_dir / "20250101_01_create_orders.py"),
            depends=set(),
        )
        m2 = FakeMigration(
            id="20250102_01_add_index",
            path=str(domain_dir / "20250102_01_add_index.py"),
            depends={"20250101_01_create_orders"},
        )
        repo = FakeRepository(migrations=[m1, m2])
        presenter = FakePresenter()

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("apply")

        data = json.loads(json_file.read_text(encoding="utf-8"))
        dep_entry = next(e for e in data if e["id"] == "20250102_01_add_index")
        assert "20250101_01_create_orders" in dep_entry["depends"]

    def test_json_export_reports_file_path(self, tmp_path):
        """Защищает от потери информационного сообщения о записи JSON."""
        root = tmp_path / "migrations"
        root.mkdir()

        json_file = tmp_path / "out.json"
        config = MigrationConfig(
            dsn="",
            migrations_root=root,
            auto_confirm=True,
            dry_run=True,
            json_plan_output_file=str(json_file),
        )

        migration = FakeMigration(
            id="A",
            path=str(root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("apply")

        assert any(str(json_file) in msg for msg in presenter.infos)
