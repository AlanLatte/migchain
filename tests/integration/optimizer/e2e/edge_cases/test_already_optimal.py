"""Full optimize cycle -- already optimal graph with multiple migrations.

- linear chain A -> B -> C has no redundancy
- optimizer reports minimal without starting testcontainer
"""

import pytest

from migchain.application.config import MigrationConfig
from migchain.application.service import MigrationService
from migchain.infrastructure.batch_tracker import PostgresBatchTracker
from migchain.infrastructure.migration_writer import FilesystemMigrationWriter
from migchain.infrastructure.schema_comparator import TestcontainerSchemaComparator
from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter
from migchain.presentation.plain import PlainPresenter


class RecordingPresenter(PlainPresenter):
    """Presenter that records calls for assertions."""

    def __init__(self) -> None:
        super().__init__()
        self.infos = []

    def info(self, message: str) -> None:
        self.infos.append(message)


@pytest.mark.integration
class TestAlreadyOptimal:
    """Protects against false positives on linear chain graphs."""

    def test_linear_chain_no_reduction(self, tmp_path):
        """Protects against optimizer modifying already-minimal linear chain."""
        root = tmp_path / "migrations"
        domain = root / "test_domain"
        domain.mkdir(parents=True)

        (domain / "0001_schema.py").write_text(
            '"""Schema."""\n'
            "from yoyo import step\n\n"
            "steps = [\n"
            '    step("CREATE SCHEMA IF NOT EXISTS test_domain"),\n'
            "]\n",
        )

        (domain / "0002_alpha.py").write_text(
            '"""Alpha."""\n'
            "from yoyo import step\n\n"
            '__depends__ = {"0001_schema"}\n\n'
            "steps = [\n"
            '    step("CREATE TABLE test_domain.alpha (id serial PRIMARY KEY)"),\n'
            "]\n",
        )

        (domain / "0003_beta.py").write_text(
            '"""Beta."""\n'
            "from yoyo import step\n\n"
            '__depends__ = {"0002_alpha"}\n\n'
            "steps = [\n"
            '    step("CREATE TABLE test_domain.beta '
            "(id serial PRIMARY KEY, "
            "alpha_id int REFERENCES "
            'test_domain.alpha(id))"),\n'
            "]\n",
        )

        presenter = RecordingPresenter()
        config = MigrationConfig(
            migrations_root=root,
            auto_confirm=True,
        )

        service = MigrationService(
            config=config,
            repository=YoyoDiscoveryAdapter(),
            backend=YoyoBackendAdapter(),
            batch_storage=PostgresBatchTracker(),
            presenter=presenter,
            schema_comparator=TestcontainerSchemaComparator(),
            migration_writer=FilesystemMigrationWriter(),
        )

        service.run("optimize")

        assert any("minimal" in m.lower() for m in presenter.infos)
        assert all("complete" not in m.lower() for m in presenter.infos)
