"""GraphVisualizer.generate_mermaid -- boundary inputs.

- empty graph -> still has "graph TD"
- unknown migration ID -> skipped in subgraphs
"""

from pathlib import Path

from migchain.domain.graph import GraphVisualizer


class TestEmptyAndMissingIds:
    """Protects against crashes on degenerate inputs: empty graphs and orphan IDs."""

    def test_empty_graph(self, migrations_root: Path) -> None:
        """Protects against crash when dependencies and migrations are both empty."""
        result = GraphVisualizer.generate_mermaid({}, {}, migrations_root)

        assert "graph TD" in result

    def test_unknown_migration_id_skipped(
        self,
        migrations_root: Path,
    ) -> None:
        """Protects against KeyError when dependency map
        references a missing migration ID."""
        deps = {"missing": set()}
        by_id: dict = {}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "missing" not in result.split("\n")[1:]  # not in subgraph body
        assert "graph TD" in result
