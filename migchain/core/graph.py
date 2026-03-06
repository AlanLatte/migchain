"""Dependency graph generation and visualization."""

from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Set

from migchain.core.analyzer import MigrationAnalyzer


class GraphGenerator:
    """Generates visualization graphs for migration dependencies."""

    @staticmethod
    def generate_mermaid_graph(
        dependencies: Dict[str, Set[str]],
        migrations_by_id: Dict[str, Any],
        migrations_root: Path,
    ) -> str:
        lines = ["graph TD"]

        domains: DefaultDict[str, List[str]] = defaultdict(list)
        for migration_id in dependencies.keys():
            if migration_id in migrations_by_id:
                domain = MigrationAnalyzer.get_migration_domain(
                    migrations_by_id[migration_id], migrations_root
                )
                domains[domain].append(migration_id)

        subgraph_counter = 0
        for domain, migration_ids in sorted(domains.items()):
            if not migration_ids:
                continue

            subgraph_counter += 1
            lines.append(f"  subgraph SG{subgraph_counter} [{domain}]")

            for migration_id in sorted(migration_ids):
                migration = migrations_by_id.get(migration_id)
                if migration:
                    category = MigrationAnalyzer.get_migration_category(migration)
                    node_style = ":::inserterNode" if category == "inserter" else ""

                    short_id = (
                        migration_id.replace(f"{domain}_", "").replace("_", "<br/>")
                        if domain != "unknown"
                        else migration_id
                    )
                    lines.append(f'    {migration_id}["{short_id}"]{node_style}')

            lines.append("  end")

        lines.append("")
        for child, parents in dependencies.items():
            for parent in parents:
                lines.append(f"  {parent} --> {child}")

        lines.extend(
            [
                "",
                "  classDef inserterNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
                "  classDef schemaNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            ]
        )

        schema_nodes = [
            migration_id
            for migration_id, migration in migrations_by_id.items()
            if MigrationAnalyzer.get_migration_category(migration) == "schema"
        ]

        if schema_nodes:
            lines.append(f"  class {','.join(schema_nodes)} schemaNode")

        return "\n".join(lines)
