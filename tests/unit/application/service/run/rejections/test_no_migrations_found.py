"""MigrationService.run -- no migration folders.

- empty repository -> SystemExit
"""

import pytest

from migchain.application.config import MigrationConfig
from tests.unit.application.conftest import FakePresenter, FakeRepository
from tests.unit.application.service.conftest import make_service


class TestNoMigrationsFound:
    """Protects against silent failure when no migration directories exist."""

    def test_raises_system_exit(self, default_config: MigrationConfig):
        """Protects against proceeding without any discovered migrations."""
        repo = FakeRepository(migrations=[])
        presenter = FakePresenter()

        svc = make_service(default_config, repository=repo, presenter=presenter)

        with pytest.raises(SystemExit, match="No migration folders"):
            svc.run("apply")
