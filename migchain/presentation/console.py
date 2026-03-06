"""Adapter: Rich console presenter."""

from pathlib import Path
from typing import Optional

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.syntax import Syntax
from rich.table import Table

from migchain.domain.analyzer import MigrationAnalyzer
from migchain.domain.models import (
    MigrationPlan,
    MigrationStructure,
    OptimizationResult,
    OptimizationVerification,
)
from migchain.domain.scaffolder import ScaffoldRequest
from migchain.infrastructure.logging import setup_logging


class RichPresenter:
    """Implements Presenter port using Rich and InquirerPy."""

    def __init__(self) -> None:
        self._console = Console()
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None
        self._verbosity = 1

    # ::::: Setup :::::
    def setup(self, verbosity: int) -> None:
        self._verbosity = verbosity
        setup_logging(verbosity)

    # ::::: Structure :::::
    def show_structure(self, structure: MigrationStructure) -> None:
        table = Table(
            title="Migration Structure",
            title_style="bold cyan",
            show_lines=True,
        )
        table.add_column("Domain", style="cyan", min_width=12)
        table.add_column("Schema", style="green", justify="right")
        table.add_column("Inserters", style="blue", justify="right")
        table.add_column("Total", style="bold", justify="right")

        for domain_name in sorted(structure.domains):
            stats = structure.domains[domain_name]
            table.add_row(
                domain_name,
                str(stats.schema_count),
                str(stats.inserter_count),
                str(stats.total),
            )

        table.add_section()
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{structure.schema_count}[/bold]",
            f"[bold]{structure.inserter_count}[/bold]",
            f"[bold]{structure.total}[/bold]",
        )

        self._console.print(table)

    # ::::: Plan :::::
    def show_plan(
        self,
        plan: MigrationPlan,
        mode: str,
        migrations_root: Optional[Path] = None,
    ) -> None:
        if plan.total_count == 0:
            self._console.print(
                Panel(
                    "[dim]Nothing to do[/dim]",
                    title=f"{mode.upper()}",
                    style="dim",
                ),
            )
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
            lines.append(
                f"  [dim]{i:3d}.[/dim] [cyan]{domain:<14}[/cyan]  {short_id}",
            )

        content = "\n".join(lines)
        self._console.print(
            Panel(
                content,
                title=f"[bold]{mode.upper()} ({plan.total_count} migrations)[/bold]",
                border_style="cyan",
            ),
        )

    # ::::: Graph :::::
    def show_graph(self, content: str) -> None:
        syntax = Syntax(content, "text", theme="monokai", line_numbers=False)
        self._console.print(
            Panel(syntax, title="Dependency Graph (Mermaid)", border_style="cyan"),
        )

    # ::::: Execution lifecycle :::::
    def start_execution(self, total: int, tag: str) -> None:
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self._console,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(tag, total=total)

    def on_migration_start(self, migration_id: str, tag: str) -> None:
        if self._progress is not None and self._task_id is not None:
            self._progress.update(
                self._task_id,
                description=f"{tag}: {migration_id}",
            )

    def on_migration_success(
        self,
        _migration_id: str,
        _tag: str,
        _duration: float,
    ) -> None:
        if self._progress is not None and self._task_id is not None:
            self._progress.advance(self._task_id)

    def on_migration_fail(self, migration_id: str, _tag: str) -> None:
        if self._progress is not None:
            self._progress.stop()
            self._progress = None
        self._console.print(
            f"  [bold red]FAIL[/bold red]  {migration_id}",
            highlight=False,
        )

    def finish_execution(self) -> None:
        if self._progress is not None:
            self._progress.stop()
            self._progress = None

    # ::::: Interactive :::::
    def confirm(self, message: str) -> bool:
        result: bool = inquirer.confirm(message=message, default=False).execute()
        return result

    # ::::: Optimization :::::
    def show_redundant_edges(self, result: OptimizationResult) -> None:
        if not result.redundant_edges:
            self._console.print(
                Panel(
                    "[green]No redundant dependencies found[/green]",
                    title="Optimization Analysis",
                    border_style="green",
                ),
            )
            return

        table = Table(
            title="Redundant Dependencies",
            title_style="bold yellow",
            show_lines=True,
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Migration", style="cyan")
        table.add_column("Redundant Dep", style="red")
        table.add_column("Alternative Path", style="green")

        for i, edge in enumerate(result.redundant_edges, 1):
            path_str = " -> ".join(edge.path) if edge.path else "?"
            table.add_row(
                str(i),
                edge.child_id,
                edge.parent_id,
                path_str,
            )

        table.add_section()
        table.add_row(
            "",
            "[bold]Total edges[/bold]",
            f"[bold]{result.original_edge_count}[/bold]",
            f"[bold]after: {result.reduced_edge_count}[/bold]",
        )

        self._console.print(table)

    def show_verification_result(
        self,
        verification: OptimizationVerification,
    ) -> None:
        if verification.is_safe:
            self._console.print(
                Panel(
                    "[bold green]Schemas are IDENTICAL "
                    "— optimization is safe[/bold green]",
                    title="Verification",
                    border_style="green",
                ),
            )
        else:
            lines = ["[bold red]Schema mismatch detected:[/bold red]", ""]
            for diff in verification.differences:
                lines.append(f"  [red]- {diff}[/red]")
            self._console.print(
                Panel(
                    "\n".join(lines),
                    title="Verification FAILED",
                    border_style="red",
                ),
            )

    # ::::: Scaffolding :::::
    def prompt_scaffold(self, existing_domains: list[str]) -> ScaffoldRequest:
        scaffold_type: str = inquirer.select(
            message="What do you want to create?",
            choices=[
                {"name": "New domain (schema + directory)", "value": "domain"},
                {"name": "Table migration", "value": "table"},
                {"name": "Inserter migration (seed data)", "value": "inserter"},
                {"name": "Free-form migration", "value": "freeform"},
            ],
        ).execute()

        if scaffold_type == "domain":
            domain: str = inquirer.text(message="Domain name:").execute()
            return ScaffoldRequest(scaffold_type="domain", domain=domain)

        domain_choices = existing_domains + ["(enter manually)"]
        selected: str = inquirer.select(
            message="Domain:",
            choices=domain_choices,
        ).execute()
        if selected == "(enter manually)":
            selected = inquirer.text(message="Domain name:").execute()

        subdirectory: str = inquirer.text(
            message="Subdirectory (e.g. users, roles):",
            default="",
        ).execute()

        description: str = inquirer.text(
            message="Description (e.g. create-table, add-index):",
        ).execute()

        return ScaffoldRequest(
            scaffold_type=scaffold_type,
            domain=selected,
            subdirectory=subdirectory,
            description=description,
        )

    # ::::: Result :::::
    def show_result(self, message: str) -> None:
        self._console.print(
            Panel(
                f"[bold green]{message}[/bold green]",
                border_style="green",
            ),
        )

    # ::::: Logging :::::
    def info(self, message: str) -> None:
        self._console.print(f"  {message}", highlight=False)

    def warning(self, message: str) -> None:
        self._console.print(
            f"  [yellow]WARN[/yellow]  {message}",
            highlight=False,
        )

    def error(self, message: str) -> None:
        self._console.print(
            Panel(message, title="Error", style="bold red"),
        )

    def debug(self, message: str) -> None:
        if self._verbosity >= 2:
            self._console.print(
                f"  [dim]DEBUG {message}[/dim]",
                highlight=False,
            )


def _short_migration_id(migration_id: str) -> str:
    """Strip date prefix from migration ID for cleaner display."""
    parts = migration_id.split("_", 2)
    if len(parts) >= 3:
        return parts[2]
    return migration_id
