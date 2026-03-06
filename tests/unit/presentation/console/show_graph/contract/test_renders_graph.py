"""RichPresenter.show_graph -- renders mermaid content in a panel.

- content appears in console output
- panel title includes 'Dependency Graph'
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.presentation.console import RichPresenter


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestRendersGraph:
    """Protects the contract of rendering mermaid graphs in a panel."""

    def test_shows_mermaid_content(self):
        """Protects against graph content not appearing in rendered output."""
        presenter = make_presenter()
        mermaid = "graph TD\n  A --> B"
        presenter.show_graph(mermaid)
        output = get_output(presenter)
        assert "A --> B" in output

    def test_panel_title_present(self):
        """Protects against the dependency graph panel missing its title."""
        presenter = make_presenter()
        presenter.show_graph("graph TD\n  X --> Y")
        output = get_output(presenter)
        assert "Dependency Graph" in output
