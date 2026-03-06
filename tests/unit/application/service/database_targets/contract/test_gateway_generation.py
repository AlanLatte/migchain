"""MigrationService._get_database_targets -- gateway DB names.

- no gw -> [None]
- gw without testing -> [None]
- gw with testing -> [None, "test_dbname__gw1", ...]
- custom template
"""
# pylint: disable=protected-access

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import FakePresenter, FakeRepository
from tests.unit.application.service.conftest import make_service


class TestGatewayGeneration:
    """Protects the database target generation for gateway configurations."""

    def test_no_gw(self, default_config: MigrationConfig):
        """Protects against non-gateway config
        producing extra targets."""
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])

        svc = make_service(default_config, repository=repo)
        targets = svc._get_database_targets()

        assert targets == [None]

    def test_gw_without_testing(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against gateway targets generated
        when testing=False."""
        default_config.gw_count = 3
        default_config.testing = False
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])

        svc = make_service(default_config, repository=repo)
        targets = svc._get_database_targets()

        assert targets == [None]

    def test_gw_with_testing(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against incorrect gateway target names
        in testing mode."""
        default_config.gw_count = 2
        default_config.testing = True
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])

        svc = make_service(default_config, repository=repo)
        targets = svc._get_database_targets()

        assert targets == [None, "test_testdb__gw1", "test_testdb__gw2"]

    def test_custom_template(
        self,
        default_config: MigrationConfig,
    ):
        """Protects against custom gw_template
        being ignored."""
        default_config.gw_count = 2
        default_config.testing = True
        default_config.gw_template = "custom_gw{i}"
        migration = FakeMigration(
            id="A",
            path=str(default_config.migrations_root / "a.py"),
        )
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        svc = make_service(default_config, repository=repo, presenter=presenter)
        targets = svc._get_database_targets()

        assert targets[1] == "custom_gw1"
