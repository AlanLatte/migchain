"""RichPresenter.show_plan -- empty plan.

- empty plan -> "Nothing to do" in output
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.domain.models import MigrationPlan
from migchain.presentation.console import RichPresenter


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestEmptyPlan:
    """Protects the contract of rendering an empty migration plan."""

    def test_shows_nothing_to_do(self):
        """Protects against empty plan not displaying 'Nothing to do' message."""
        presenter = make_presenter()
        plan = MigrationPlan()
        presenter.show_plan(plan, mode="apply")
        output = get_output(presenter)
        assert "Nothing to do" in output
