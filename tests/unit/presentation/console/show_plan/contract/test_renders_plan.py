"""RichPresenter.show_plan -- non-empty plan rendering.

- displays migration IDs
- displays operation mode in uppercase
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


class TestRendersPlan:
    """Protects the contract of rendering non-empty migration plans."""

    def test_shows_migration_ids(self):
        """Protects against migration IDs not appearing in rendered output."""
        presenter = make_presenter()
        migration = FakeMigration(id="20250101_01_create_users")
        plan = MigrationPlan(
            schema_migrations=[migration],
            all_migrations=[migration],
        )
        presenter.show_plan(plan, mode="apply")
        output = get_output(presenter)
        assert "create_users" in output

    def test_shows_mode_uppercase(self):
        """Protects against operation mode not being displayed in uppercase."""
        presenter = make_presenter()
        migration = FakeMigration(id="0001_init")
        plan = MigrationPlan(
            schema_migrations=[migration],
            all_migrations=[migration],
        )
        presenter.show_plan(plan, mode="apply")
        output = get_output(presenter)
        assert "APPLY" in output
