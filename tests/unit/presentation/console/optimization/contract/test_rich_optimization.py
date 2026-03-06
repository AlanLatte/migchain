"""RichPresenter -- optimization output methods.

- show_redundant_edges renders a Rich table
- show_verification_result shows safe/unsafe panel
- no redundancy -> green panel
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.domain.models import (
    OptimizationResult,
    OptimizationVerification,
    RedundantEdge,
)
from migchain.presentation.console import RichPresenter


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestRichOptimization:
    """Protects the contract of Rich-formatted optimization output."""

    def test_show_redundant_edges_table(self):
        """Protects against redundant edges not appearing in output."""
        presenter = make_presenter()
        result = OptimizationResult(
            original_edge_count=5,
            reduced_edge_count=3,
            redundant_edges=[
                RedundantEdge(
                    child_id="D",
                    parent_id="A",
                    path=["D", "C", "B", "A"],
                ),
                RedundantEdge(
                    child_id="E",
                    parent_id="B",
                    path=["E", "C", "B"],
                ),
            ],
        )
        presenter.show_redundant_edges(result)
        output = get_output(presenter)
        assert "D" in output
        assert "A" in output

    def test_show_no_redundancy(self):
        """Protects against empty result not showing green panel."""
        presenter = make_presenter()
        result = OptimizationResult(
            original_edge_count=3,
            reduced_edge_count=3,
        )
        presenter.show_redundant_edges(result)
        output = get_output(presenter)
        assert "No redundant" in output

    def test_show_verification_safe(self):
        """Protects against safe verification not being displayed as green."""
        presenter = make_presenter()
        presenter.show_verification_result(
            OptimizationVerification(is_safe=True),
        )
        output = get_output(presenter)
        assert "IDENTICAL" in output

    def test_show_verification_unsafe(self):
        """Protects against unsafe verification not showing differences."""
        presenter = make_presenter()
        presenter.show_verification_result(
            OptimizationVerification(
                is_safe=False,
                differences=["[tables] differs: users"],
            ),
        )
        output = get_output(presenter)
        assert "FAILED" in output
        assert "users" in output
