"""Domain service: dependency graph visualization."""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from migchain.domain.analyzer import MigrationAnalyzer


class GraphVisualizer:
    """Pure domain logic for generating Mermaid dependency graphs."""

    @staticmethod
    def generate_mermaid(
        dependencies: Dict[str, Set[str]],
        migrations_by_id: Dict[str, Any],
        migrations_root: Path,
    ) -> str:
        lines = ["graph TD"]

        # ::::: Group by domain :::::
        domains: dict[str, List[str]] = defaultdict(list)
        for mid in dependencies:
            if mid in migrations_by_id:
                domain = MigrationAnalyzer.get_migration_domain(
                    migrations_by_id[mid],
                    migrations_root,
                )
                domains[domain].append(mid)

        # ::::: Subgraphs :::::
        counter = 0
        for domain, mids in sorted(domains.items()):
            if not mids:  # pragma: no cover
                continue
            counter += 1
            lines.append(f"  subgraph SG{counter} [{domain}]")

            for mid in sorted(mids):
                migration = migrations_by_id.get(mid)
                if migration:
                    cat = MigrationAnalyzer.get_migration_category(migration)
                    style = ":::inserterNode" if cat == "inserter" else ""
                    short = (
                        mid.replace(f"{domain}_", "").replace("_", "<br/>")
                        if domain != "unknown"
                        else mid
                    )
                    lines.append(f'    {mid}["{short}"]{style}')
            lines.append("  end")

        # ::::: Edges :::::
        lines.append("")
        for child, parents in dependencies.items():
            for parent in parents:
                lines.append(f"  {parent} --> {child}")

        # ::::: Styling :::::
        lines.extend(
            [
                "",
                "  classDef inserterNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
                "  classDef schemaNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            ],
        )

        schema_nodes = [
            mid
            for mid, m in migrations_by_id.items()
            if MigrationAnalyzer.get_migration_category(m) == "schema"
        ]
        if schema_nodes:
            joined = ",".join(schema_nodes)
            lines.append(f"  class {joined} schemaNode")

        return "\n".join(lines)
