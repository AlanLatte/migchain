"""GraphVisualizer.generate_mermaid -- valid Mermaid output.

- starts with "graph TD"
- subgraph labeled with domain name
- inserter nodes get :::inserterNode class
- schema nodes get schemaNode class applied
- edges A --> B generated
- multiple domains create separate subgraphs
- classDef styling lines present
- diamond edges all rendered
"""

from pathlib import Path

from migchain.domain.graph import GraphVisualizer
from tests.conftest import FakeMigration


class TestGeneratesValidMermaid:
    """Protects the core contract: generate_mermaid produces
    syntactically valid Mermaid output."""

    def test_starts_with_graph_td(self, migrations_root: Path) -> None:
        """Protects against missing Mermaid graph header."""
        m = FakeMigration(
            id="A",
            path=str(migrations_root / "auth" / "users" / "A.py"),
        )
        deps = {"A": set()}
        by_id = {"A": m}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert result.startswith("graph TD")

    def test_subgraph_contains_domain(self, migrations_root: Path) -> None:
        """Protects against domain label missing from subgraph header."""
        m = FakeMigration(
            id="A",
            path=str(migrations_root / "auth" / "users" / "A.py"),
        )
        deps = {"A": set()}
        by_id = {"A": m}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "[auth]" in result

    def test_inserter_gets_inserter_class(self, migrations_root: Path) -> None:
        """Protects against inserter nodes losing their Mermaid class annotation."""
        m = FakeMigration(
            id="seed",
            path=str(migrations_root / "billing" / "plans" / "inserters" / "seed.py"),
        )
        deps = {"seed": set()}
        by_id = {"seed": m}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert ":::inserterNode" in result

    def test_schema_gets_schema_class(self, migrations_root: Path) -> None:
        """Protects against schema nodes missing the schemaNode class assignment."""
        m = FakeMigration(
            id="create_table",
            path=str(migrations_root / "auth" / "users" / "create_table.py"),
        )
        deps = {"create_table": set()}
        by_id = {"create_table": m}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "schemaNode" in result

    def test_edges_generated(self, migrations_root: Path) -> None:
        """Protects against dependency edges being omitted from output."""
        a = FakeMigration(
            id="A",
            path=str(migrations_root / "auth" / "users" / "A.py"),
        )
        b = FakeMigration(
            id="B",
            path=str(migrations_root / "auth" / "users" / "B.py"),
        )
        deps = {"A": set(), "B": {"A"}}
        by_id = {"A": a, "B": b}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "A --> B" in result

    def test_multiple_domains_separate_subgraphs(
        self,
        migrations_root: Path,
    ) -> None:
        """Protects against migrations from different domains
        being grouped into one subgraph."""
        m_auth = FakeMigration(
            id="auth_m",
            path=str(migrations_root / "auth" / "users" / "auth_m.py"),
        )
        m_billing = FakeMigration(
            id="billing_m",
            path=str(
                migrations_root / "billing" / "plans" / "inserters" / "billing_m.py",
            ),
        )
        deps = {"auth_m": set(), "billing_m": set()}
        by_id = {"auth_m": m_auth, "billing_m": m_billing}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "[auth]" in result
        assert "[billing]" in result

    def test_class_def_styling_present(self, migrations_root: Path) -> None:
        """Protects against missing classDef declarations for node styling."""
        m = FakeMigration(
            id="A",
            path=str(migrations_root / "auth" / "users" / "A.py"),
        )
        deps = {"A": set()}
        by_id = {"A": m}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "classDef inserterNode" in result
        assert "classDef schemaNode" in result

    def test_diamond_edges(self, diamond_chain: list, migrations_root: Path) -> None:
        """Protects against incomplete edge rendering in diamond dependency graphs."""
        by_id = {m.id: m for m in diamond_chain}
        deps = {m.id: m.depends for m in diamond_chain}

        result = GraphVisualizer.generate_mermaid(deps, by_id, migrations_root)

        assert "A --> B" in result
        assert "A --> C" in result
        assert "B --> D" in result
        assert "C --> D" in result
