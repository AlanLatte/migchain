"""RichPresenter.show_structure -- migration structure table.

- renders table with domain name and "Migration Structure" title
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.domain.models import DomainStats, MigrationStructure
from migchain.presentation.console import RichPresenter


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestRendersTable:
    """Protects the contract of rendering migration structure as a Rich table."""

    def test_renders_structure(self):
        """Protects against domain names and table title not appearing in output."""
        presenter = make_presenter()
        structure = MigrationStructure(
            total=3,
            schema_count=2,
            inserter_count=1,
            domains={
                "auth": DomainStats(
                    schema_count=2,
                    inserter_count=1,
                    migration_ids=["0001_init", "0002_roles", "0003_seed"],
                ),
            },
        )
        presenter.show_structure(structure)
        output = get_output(presenter)
        assert "auth" in output
        assert "Migration Structure" in output
