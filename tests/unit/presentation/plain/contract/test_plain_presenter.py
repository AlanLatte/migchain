"""PlainPresenter -- behavioral contract.

- show_plan renders migration IDs, inserters, empty plans
- show_structure renders domain table
- show_graph renders mermaid content
- show_redundant_edges renders optimization table
- show_verification_result reports safety
- confirm accepts y/yes, rejects everything else
"""

import logging
from unittest.mock import patch

from migchain.domain.models import (
    DomainStats,
    MigrationPlan,
    MigrationStructure,
    OptimizationResult,
    OptimizationVerification,
    RedundantEdge,
)
from migchain.presentation.plain import PlainPresenter
from tests.conftest import FakeMigration


class TestPlainPresenter:
    """Protects the behavioral contract of the Presenter port."""

    def test_show_structure_renders_domains(self, caplog):
        """Protects against structure table not rendering domain stats."""
        presenter = PlainPresenter()
        structure = MigrationStructure(
            total=3,
            schema_count=2,
            inserter_count=1,
            domains={
                "auth": DomainStats(schema_count=2, inserter_count=0),
                "billing": DomainStats(schema_count=0, inserter_count=1),
            },
        )
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_structure(structure)
        assert "auth" in caplog.text
        assert "billing" in caplog.text

    def test_show_plan_renders_ids(self, caplog):
        """Protects against migration IDs missing from plan output."""
        presenter = PlainPresenter()
        migration = FakeMigration(id="20250101_01_create_users")
        plan = MigrationPlan(
            schema_migrations=[migration],
            all_migrations=[migration],
        )
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_plan(plan, "apply")
        assert "create_users" in caplog.text
        assert "APPLY" in caplog.text

    def test_show_plan_shows_domain(self, caplog):
        """Protects against domain name missing from plan output."""
        presenter = PlainPresenter()
        migration = FakeMigration(id="20250101_01_seed")
        plan = MigrationPlan(
            inserter_migrations=[migration],
            all_migrations=[migration],
        )
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_plan(plan, "apply")
        assert "unknown" in caplog.text

    def test_show_plan_empty(self, caplog):
        """Protects against empty plan not showing 'Nothing to do'."""
        presenter = PlainPresenter()
        plan = MigrationPlan()
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_plan(plan, "apply")
        assert "Nothing to do" in caplog.text

    def test_show_graph(self, caplog):
        """Protects against graph content not being rendered."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_graph("graph TD\n  A --> B")
        assert "A --> B" in caplog.text

    def test_show_redundant_edges(self, caplog):
        """Protects against redundant edges table not rendering."""
        presenter = PlainPresenter()
        result = OptimizationResult(
            original_edge_count=5,
            reduced_edge_count=3,
            redundant_edges=[
                RedundantEdge(
                    child_id="D",
                    parent_id="A",
                    path=["D", "C", "B", "A"],
                ),
            ],
        )
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_redundant_edges(result)
        assert "D" in caplog.text
        assert "A" in caplog.text

    def test_show_redundant_edges_empty(self, caplog):
        """Protects against empty optimization result not being reported."""
        presenter = PlainPresenter()
        result = OptimizationResult(
            original_edge_count=3,
            reduced_edge_count=3,
        )
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_redundant_edges(result)
        assert "No redundant" in caplog.text

    def test_show_verification_safe(self, caplog):
        """Protects against safe verification not being clearly reported."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_verification_result(
                OptimizationVerification(is_safe=True),
            )
        assert "IDENTICAL" in caplog.text

    def test_show_verification_unsafe(self, caplog):
        """Protects against unsafe verification not showing differences."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.ERROR, logger="migchain"):
            presenter.show_verification_result(
                OptimizationVerification(
                    is_safe=False,
                    differences=["[tables] differs: users"],
                ),
            )
        assert "FAILED" in caplog.text
        assert "users" in caplog.text

    def test_confirm_accepts_y(self):
        """Protects against 'y' not being accepted as confirmation."""
        presenter = PlainPresenter()
        with patch("builtins.input", return_value="y"):
            assert presenter.confirm("Proceed?") is True

    def test_confirm_accepts_yes(self):
        """Protects against 'yes' not being accepted as confirmation."""
        presenter = PlainPresenter()
        with patch("builtins.input", return_value="yes"):
            assert presenter.confirm("Proceed?") is True

    def test_confirm_rejects_n(self):
        """Protects against empty input being treated as confirmation."""
        presenter = PlainPresenter()
        with patch("builtins.input", return_value=""):
            assert presenter.confirm("Proceed?") is False
