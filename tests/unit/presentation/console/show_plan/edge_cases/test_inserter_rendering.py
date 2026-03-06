"""RichPresenter.show_plan -- inserter migration rendering.

- inserter migration gets blue 'inserter' tag
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.domain.models import MigrationPlan
from migchain.presentation.console import RichPresenter
from tests.conftest import FakeMigration


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestInserterRendering:
    """Protects the visual distinction between inserter and schema migrations."""

    def test_inserter_migration_tagged(self):
        """Protects against inserter migrations not being visually differentiated."""
        presenter = make_presenter()
        schema = FakeMigration(id="0001_create_users")
        inserter = FakeMigration(id="0002_seed_data")
        plan = MigrationPlan(
            schema_migrations=[schema],
            inserter_migrations=[inserter],
            all_migrations=[schema, inserter],
        )
        presenter.show_plan(plan, mode="apply")
        output = get_output(presenter)
        assert "0002_seed_data" in output
        assert "inserter" in output
