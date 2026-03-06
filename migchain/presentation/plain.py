"""Adapter: plain-text console presenter (no external dependencies)."""

import logging
import textwrap
from pathlib import Path
from typing import Optional

from migchain.constants import LOGGER_NAME
from migchain.domain.analyzer import MigrationAnalyzer
from migchain.domain.models import (
    MigrationPlan,
    MigrationStructure,
    OptimizationResult,
    OptimizationVerification,
)
from migchain.domain.scaffolder import ScaffoldRequest
from migchain.infrastructure.logging import setup_logging

LOGGER = logging.getLogger(LOGGER_NAME)


class PlainPresenter:
    """Implements Presenter port using standard logging output."""

    def __init__(self) -> None:
        self._verbosity = 1

    # ::::: Setup :::::
    def setup(self, verbosity: int) -> None:
        self._verbosity = verbosity
        setup_logging(verbosity)

    # ::::: Structure :::::
    def show_structure(self, structure: MigrationStructure) -> None:
        domain = "Domain"
        schema = "Schema"
        ins = "Inserters"
        total = "Total"
        header = f"{domain:<20} {schema:>8} {ins:>10} {total:>8}"
        separator = "-" * 48
        lines = [header, separator]

        for domain_name in sorted(structure.domains):
            stats = structure.domains[domain_name]
            lines.append(
                f"{domain_name:<20} {stats.schema_count:>8} "
                f"{stats.inserter_count:>10} {stats.total:>8}",
            )

        lines.append(separator)
        total_label = "Total"
        lines.append(
            f"{total_label:<20} {structure.schema_count:>8} "
            f"{structure.inserter_count:>10} {structure.total:>8}",
        )

        LOGGER.info("Migration Structure\n%s", "\n".join(lines))

    # ::::: Plan :::::
    def show_plan(
        self,
        plan: MigrationPlan,
        mode: str,
        migrations_root: Optional[Path] = None,
    ) -> None:
        if plan.total_count == 0:
            LOGGER.info("[%s] Nothing to do", mode.upper())
            return

        lines = []
        for i, migration in enumerate(plan.all_migrations, 1):
            domain = "unknown"
            if migrations_root:
                domain = MigrationAnalyzer.get_migration_domain(
                    migration,
                    migrations_root,
                )
            short_id = _short_migration_id(migration.id)
            lines.append(f"  {i:3d}. [{domain:<14}]  {short_id}")

        LOGGER.info(
            "%s (%d migrations)\n%s",
            mode.upper(),
            plan.total_count,
            "\n".join(lines),
        )

    # ::::: Graph :::::
    def show_graph(self, content: str) -> None:
        LOGGER.info("Dependency Graph (Mermaid)\n%s", content)

    # ::::: Execution lifecycle :::::
    def start_execution(self, total: int, tag: str) -> None:
        LOGGER.info("Starting %s (%d migrations)...", tag, total)

    def on_migration_start(  # pragma: no cover
        self,
        migration_id: str,
        tag: str,
    ) -> None:
        pass

    def on_migration_success(  # pragma: no cover
        self,
        migration_id: str,
        _tag: str,
        duration: float,
    ) -> None:
        LOGGER.info("OK    %s (%.2fs)", migration_id, duration)

    def on_migration_fail(  # pragma: no cover
        self,
        migration_id: str,
        _tag: str,
    ) -> None:
        LOGGER.error("FAIL  %s", migration_id)

    def finish_execution(self) -> None:  # pragma: no cover
        LOGGER.info("Done.")

    # ::::: Interactive :::::
    def confirm(self, message: str) -> bool:
        answer = input(f"  {message} [y/N]: ").strip().lower()
        return answer in ("y", "yes")

    # ::::: Optimization :::::
    def show_redundant_edges(self, result: OptimizationResult) -> None:
        if not result.redundant_edges:
            LOGGER.info("No redundant dependencies found.")
            return

        num = "#"
        mig = "Migration"
        dep = "Redundant Dep"
        header = f"{num:>3}  {mig:<40} {dep:<30} Alternative Path"
        separator = "-" * 90
        lines = [header, separator]

        for i, edge in enumerate(result.redundant_edges, 1):
            path_str = " -> ".join(edge.path) if edge.path else "?"
            lines.append(
                f"{i:3d}  {edge.child_id:<40} {edge.parent_id:<30} {path_str}",
            )

        orig = result.original_edge_count
        reduced = result.reduced_edge_count
        lines.append(f"\nTotal edges: {orig} -> {reduced}")

        LOGGER.info("Redundant Dependencies\n%s", "\n".join(lines))

    def show_verification_result(
        self,
        verification: OptimizationVerification,
    ) -> None:
        if verification.is_safe:
            LOGGER.info(
                "Verification: schemas are IDENTICAL — optimization is safe.",
            )
        else:
            diff_lines = "\n".join(f"  - {d}" for d in verification.differences)
            LOGGER.error(
                "Verification FAILED — schema mismatch:\n%s",
                diff_lines,
            )

    # ::::: Scaffolding :::::
    def prompt_scaffold(self, existing_domains: list[str]) -> ScaffoldRequest:
        LOGGER.info("Select migration type:")
        options = [
            ("1", "New domain (schema + directory)", "domain"),
            ("2", "Table migration", "table"),
            ("3", "Inserter migration (seed data)", "inserter"),
            ("4", "Free-form migration", "freeform"),
        ]
        for num, label, _ in options:
            LOGGER.info("  %s. %s", num, label)

        choice = input("Choice [1-4]: ").strip()
        type_map = {o[0]: o[2] for o in options}
        scaffold_type = type_map.get(choice, "freeform")

        if scaffold_type == "domain":
            domain = input("Domain name: ").strip()
            return ScaffoldRequest(scaffold_type="domain", domain=domain)

        if existing_domains:
            LOGGER.info("Existing domains: %s", ", ".join(existing_domains))
        domain = input("Domain name: ").strip()
        subdirectory = input("Subdirectory (e.g. users, roles): ").strip()
        description = input("Description (e.g. create-table, add-index): ").strip()

        return ScaffoldRequest(
            scaffold_type=scaffold_type,
            domain=domain,
            subdirectory=subdirectory,
            description=description,
        )

    # ::::: Result :::::
    def show_result(self, message: str) -> None:
        LOGGER.info(message)

    # ::::: Logging :::::
    def info(self, message: str) -> None:
        LOGGER.info(message)

    def warning(self, message: str) -> None:  # pragma: no cover
        LOGGER.warning(message)

    def error(self, message: str) -> None:  # pragma: no cover
        border = "=" * 60
        wrapped = textwrap.fill(message, width=56)
        LOGGER.error("%s\n%s\n%s", border, wrapped, border)

    def debug(self, message: str) -> None:
        LOGGER.debug(message)


def _short_migration_id(migration_id: str) -> str:
    """Strip date prefix from migration ID for cleaner display."""
    parts = migration_id.split("_", 2)
    if len(parts) >= 3:
        return parts[2]
    return migration_id
