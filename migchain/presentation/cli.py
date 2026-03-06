"""Adapter: CLI argument parsing."""

import argparse
import os
import textwrap
from pathlib import Path
from typing import Any, List, Set

from migchain.application.config import MigrationConfig
from migchain.constants import DEFAULT_DOMAIN_LEVEL

try:
    from InquirerPy import inquirer
    from InquirerPy.separator import Separator

    OPERATION_CHOICES: List[Any] = [
        {"name": "Apply pending migrations", "value": "apply"},
        {"name": "Rollback all migrations", "value": "rollback"},
        {"name": "Rollback one (safest leaf)", "value": "rollback-one"},
        {"name": "Rollback latest batch", "value": "rollback-latest"},
        Separator(),
        {"name": "Full reload (rollback + apply)", "value": "reload"},
        {"name": "Optimize dependencies (transitive reduction)", "value": "optimize"},
        Separator(),
        {"name": "Create new migration", "value": "new"},
    ]
    _HAS_INQUIRER = True
except ImportError:  # pragma: no cover
    _HAS_INQUIRER = False
    OPERATION_CHOICES = []


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migchain",
        description="Database Migration Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              %(prog)s --apply                    # Apply pending migrations
              %(prog)s --rollback                 # Rollback all migrations
              %(prog)s --rollback-latest          # Rollback latest batch
              %(prog)s --dry-run -vv              # Show what would be executed
              %(prog)s --include auth,orders      # Only process specific domains
        """),
    )

    # ::::: Connection :::::
    conn = parser.add_argument_group("Connection")
    conn.add_argument(
        "--dsn",
        help="PostgreSQL connection string (fallback: DATABASE_URL env var)",
    )
    conn.add_argument(
        "--migrations-dir",
        default="./migrations",
        help="Path to migrations root (default: %(default)s)",
    )

    # ::::: Operation mode :::::
    ops = parser.add_mutually_exclusive_group()
    ops.add_argument("--apply", action="store_true", help="Apply pending migrations")
    ops.add_argument("--rollback", action="store_true", help="Rollback all")
    ops.add_argument("--rollback-one", action="store_true", help="Rollback one leaf")
    ops.add_argument(
        "--rollback-latest",
        action="store_true",
        help="Rollback latest batch",
    )
    ops.add_argument("--reload", action="store_true", help="Full reload")
    ops.add_argument(
        "--optimize",
        action="store_true",
        help="Optimize deps via transitive reduction",
    )
    ops.add_argument(
        "--new",
        action="store_true",
        help="Create new migration (interactive)",
    )

    # ::::: Execution :::::
    ex = parser.add_argument_group("Execution")
    ex.add_argument("--dry-run", action="store_true", help="Show plan only")
    ex.add_argument("--no-inserters", action="store_true", help="Skip inserters")
    ex.add_argument("-y", "--yes", action="store_true", help="Skip confirmations")

    # ::::: Filtering :::::
    filt = parser.add_argument_group("Filtering")
    filt.add_argument("--include", help="Comma-separated domains to include")
    filt.add_argument("--exclude", help="Comma-separated domains to exclude")
    filt.add_argument(
        "--domain-level",
        type=int,
        default=DEFAULT_DOMAIN_LEVEL,
        help="Directory level for domain filtering (default: %(default)s)",
    )

    # ::::: Output :::::
    out = parser.add_argument_group("Output")
    out.add_argument(
        "--show-structure",
        action="store_true",
        help="Show structure table",
    )
    out.add_argument("--show-graph", action="store_true", help="Show dependency graph")
    out.add_argument("--graph-out", help="Write graph to file (Mermaid)")
    out.add_argument("--json-plan-out", help="Export plan to JSON")

    # ::::: Verbosity :::::
    verb = parser.add_argument_group("Verbosity")
    verb.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Increase verbosity",
    )
    verb.add_argument("-q", "--quiet", action="store_true", help="Warnings only")

    # ::::: Environment :::::
    env = parser.add_argument_group("Environment")
    env.add_argument("--testing", action="store_true", help="Use test DB")
    env.add_argument(
        "--gw-count",
        type=int,
        help="Gateway DB count (requires --testing)",
    )
    env.add_argument("--gw-template", help="Gateway DB name template")

    return parser


def resolve_operation(args: argparse.Namespace) -> str:
    """Determine operation mode — interactive if none specified."""
    if args.rollback:
        return "rollback"
    if args.rollback_one:
        return "rollback-one"
    if args.rollback_latest:
        return "rollback-latest"
    if args.reload:
        return "reload"
    if args.optimize:
        return "optimize"
    if args.new:
        return "new"
    if args.apply:
        return "apply"

    if not _HAS_INQUIRER:
        return "apply"

    result: str = inquirer.select(
        message="Select operation:",
        choices=OPERATION_CHOICES,
        default="apply",
    ).execute()
    return result


def build_config(args: argparse.Namespace) -> MigrationConfig:
    """Build MigrationConfig from parsed args + env vars."""
    dsn = args.dsn or os.environ.get("DATABASE_URL", "")
    if not dsn and not args.dry_run and not args.optimize and not args.new:
        raise SystemExit(
            "Database connection string required. "
            "Use --dsn or set DATABASE_URL environment variable.",
        )

    if args.gw_count is not None and not args.testing:
        raise SystemExit("--gw-count requires --testing flag")
    if args.gw_template is not None and args.gw_count is None:
        raise SystemExit("--gw-template requires --gw-count flag")

    verbosity = 0 if args.quiet else min(args.verbose, 2)

    include_domains: Set[str] | None = None
    if args.include:
        include_domains = {d.strip() for d in args.include.split(",")}

    exclude_domains: Set[str] | None = None
    if args.exclude:
        exclude_domains = {d.strip() for d in args.exclude.split(",")}

    migrations_root = Path(args.migrations_dir).resolve()
    if args.new:
        migrations_root.mkdir(parents=True, exist_ok=True)
    elif not migrations_root.is_dir():
        raise SystemExit(f"Migrations directory not found: {migrations_root}")

    return MigrationConfig(
        dsn=dsn,
        migrations_root=migrations_root,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        domain_level=args.domain_level,
        run_inserters=not args.no_inserters,
        dry_run=args.dry_run,
        testing=args.testing,
        verbose=verbosity >= 2,
        auto_confirm=args.yes,
        show_structure=args.show_structure,
        show_graph=args.show_graph,
        graph_output_file=args.graph_out,
        json_plan_output_file=args.json_plan_out,
        gw_count=args.gw_count,
        gw_template=args.gw_template,
    )
