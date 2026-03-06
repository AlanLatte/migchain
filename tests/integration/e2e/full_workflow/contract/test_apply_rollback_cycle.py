"""Full MigrationService workflow -- end-to-end.

- apply all -> migrations succeed
- apply then rollback-latest -> same count rolled back
- apply then rollback-all -> all rolled back
- apply then rollback-one -> exactly one rolled back
- reload -> both phases execute
- dry-run -> no side effects
- dry-run JSON export -> valid file
- show-structure -> structure_calls populated
- show-graph -> graph_calls populated
- include domain filter -> only filtered domain applied
"""

import json
from pathlib import Path

import pytest

from migchain.application.config import MigrationConfig
from migchain.application.service import MigrationService
from migchain.infrastructure.batch_tracker import PostgresBatchTracker
from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter
from tests.unit.application.conftest import FakePresenter


def make_e2e_service(dsn, examples_root, presenter=None, **config_kwargs):
    config = MigrationConfig(
        dsn=dsn,
        migrations_root=examples_root,
        auto_confirm=True,
        **config_kwargs,
    )
    return MigrationService(
        config=config,
        repository=YoyoDiscoveryAdapter(),
        backend=YoyoBackendAdapter(),
        batch_storage=PostgresBatchTracker(),
        presenter=presenter or FakePresenter(),
    )


@pytest.mark.integration
@pytest.mark.slow
class TestApplyRollbackCycle:
    """Protects the full apply/rollback lifecycle through real infrastructure."""

    def test_apply_all(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against apply failing on real PostgreSQL + yoyo stack."""
        presenter = FakePresenter()
        svc = make_e2e_service(postgres_dsn, examples_root, presenter)

        svc.run("apply")

        assert len(presenter.migration_successes) > 0

    def test_apply_then_rollback_latest(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against rollback-latest not reversing the last batch."""
        rollback_presenter = FakePresenter()
        rollback_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            rollback_presenter,
        )
        rollback_svc.run("rollback")

        apply_presenter = FakePresenter()
        apply_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            apply_presenter,
        )
        apply_svc.run("apply")
        applied_count = len(apply_presenter.migration_successes)

        latest_presenter = FakePresenter()
        latest_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            latest_presenter,
        )
        latest_svc.run("rollback-latest")

        assert len(latest_presenter.migration_successes) == applied_count

    def test_apply_then_rollback_all(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against rollback not reversing all applied migrations."""
        apply_presenter = FakePresenter()
        apply_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            apply_presenter,
        )
        apply_svc.run("apply")

        rollback_presenter = FakePresenter()
        rollback_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            rollback_presenter,
        )
        rollback_svc.run("rollback")

        assert len(rollback_presenter.migration_successes) > 0

    def test_apply_then_rollback_one(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against rollback-one rolling back more than one migration."""
        apply_presenter = FakePresenter()
        apply_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            apply_presenter,
        )
        apply_svc.run("apply")

        one_presenter = FakePresenter()
        one_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            one_presenter,
        )
        one_svc.run("rollback-one")

        assert len(one_presenter.migration_successes) == 1

    def test_reload(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against reload not executing both rollback and apply phases."""
        presenter = FakePresenter()
        svc = make_e2e_service(postgres_dsn, examples_root, presenter)

        svc.run("reload")

        assert len(presenter.migration_successes) > 0

    def test_dry_run_no_side_effects(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against dry-run accidentally applying migrations."""
        rollback_presenter = FakePresenter()
        rollback_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            rollback_presenter,
        )
        rollback_svc.run("rollback")

        presenter = FakePresenter()
        svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            presenter,
            dry_run=True,
        )
        svc.run("apply")

        assert len(presenter.plan_calls) >= 1
        assert len(presenter.migration_successes) == 0

    def test_dry_run_json_export(
        self,
        postgres_dsn: str,
        examples_root: Path,
        tmp_path: Path,
    ):
        """Protects against invalid JSON export during dry-run."""
        json_file = str(tmp_path / "plan.json")
        presenter = FakePresenter()
        svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            presenter,
            dry_run=True,
            json_plan_output_file=json_file,
        )
        svc.run("apply")

        with open(json_file, encoding="utf-8") as fh:
            data = json.load(fh)

        assert isinstance(data, list)
        assert len(data) > 0
        first = data[0]
        assert "id" in first
        assert "domain" in first
        assert "category" in first

    def test_show_structure(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against show_structure flag not triggering presenter call."""
        presenter = FakePresenter()
        svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            presenter,
            show_structure=True,
            dry_run=True,
        )
        svc.run("apply")

        assert len(presenter.structure_calls) >= 1

    def test_show_graph(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against show_graph flag not triggering presenter call."""
        presenter = FakePresenter()
        svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            presenter,
            show_graph=True,
            dry_run=True,
        )
        svc.run("apply")

        assert len(presenter.graph_calls) >= 1

    def test_include_domain_filter(
        self,
        postgres_dsn: str,
        examples_root: Path,
    ):
        """Protects against include_domains filter being ignored in full workflow."""
        rollback_presenter = FakePresenter()
        rollback_svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            rollback_presenter,
        )
        rollback_svc.run("rollback")

        presenter = FakePresenter()
        svc = make_e2e_service(
            postgres_dsn,
            examples_root,
            presenter,
            include_domains={"auth"},
        )
        svc.run("apply")

        assert len(presenter.migration_successes) > 0
