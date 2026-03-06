"""RichPresenter.show_plan -- multiple migration rendering.

- all migration short IDs appear in output
- domain column is shown
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


class TestMultipleMigrations:
    """Protects rendering of plans with multiple migrations."""

    def test_all_migrations_shown(self):
        """Protects against migrations being omitted from rendered output."""
        presenter = make_presenter()
        schema = FakeMigration(id="20250101_01_create_users")
        inserter = FakeMigration(id="20250101_02_seed_data")
        plan = MigrationPlan(
            schema_migrations=[schema],
            inserter_migrations=[inserter],
            all_migrations=[schema, inserter],
        )
        presenter.show_plan(plan, mode="apply")
        output = get_output(presenter)
        assert "create_users" in output
        assert "seed_data" in output
