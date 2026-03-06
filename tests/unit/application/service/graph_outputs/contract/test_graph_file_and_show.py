"""MigrationService._generate_graph_outputs -- file output and show.

- show_graph flag -> presenter.show_graph called
- graph_output_file -> writes mermaid to file
"""

from migchain.application.config import MigrationConfig
from tests.conftest import FakeMigration
from tests.unit.application.conftest import (
    FakePresenter,
    FakeRepository,
)
from tests.unit.application.service.conftest import make_service


class TestGraphFileAndShow:
    """Protects graph output rendering and file writing paths."""

    def test_show_graph_calls_presenter(self, tmp_path):
        """Protects against show_graph flag being silently ignored."""
        root = tmp_path / "migrations"
        root.mkdir()
        migration = FakeMigration(id="A", path=str(root / "a.py"))
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        config = MigrationConfig(
            dsn="postgresql://u:p@localhost:5432/db",
            migrations_root=root,
            auto_confirm=True,
            dry_run=True,
            show_graph=True,
        )

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("apply")

        assert len(presenter.graph_calls) == 1
        assert "graph TD" in presenter.graph_calls[0]

    def test_graph_output_file_writes_mermaid(self, tmp_path):
        """Protects against graph_output_file not writing content to disk."""
        root = tmp_path / "migrations"
        root.mkdir()
        graph_file = tmp_path / "graph.mmd"
        migration = FakeMigration(id="A", path=str(root / "a.py"))
        repo = FakeRepository(migrations=[migration])
        presenter = FakePresenter()

        config = MigrationConfig(
            dsn="postgresql://u:p@localhost:5432/db",
            migrations_root=root,
            auto_confirm=True,
            dry_run=True,
            graph_output_file=str(graph_file),
        )

        svc = make_service(config, repository=repo, presenter=presenter)
        svc.run("apply")

        assert graph_file.exists()
        content = graph_file.read_text()
        assert "graph TD" in content
        assert any("graph written" in m.lower() for m in presenter.infos)
