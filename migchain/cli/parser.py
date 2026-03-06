"""Command-line interface parsing."""

import argparse
import os
import textwrap
from pathlib import Path
from typing import Set

from migchain.constants import DEFAULT_DOMAIN_LEVEL
from migchain.core.config import MigrationConfig


class CLIParser:
    """Handles command-line interface parsing and validation."""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="migchain",
            description="Database Migration Management Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(
                """
                Examples:
                  %(prog)s --apply                    # Apply pending migrations
                  %(prog)s --rollback                 # Rollback all migrations
                  %(prog)s --rollback-one             # Rollback one safe migration
                  %(prog)s --rollback-latest          # Rollback latest applied migration
                  %(prog)s --reload --no-inserters    # Reload schema migrations only
                  %(prog)s --dry-run --verbose        # Show what would be executed
                  %(prog)s --include auth,orders      # Only process specific domains
            """
            ),
        )

        # ::::: Connection :::::
        connection_group = parser.add_argument_group("Connection")
        connection_group.add_argument(
            "--dsn",
            help="PostgreSQL connection string (fallback: DATABASE_URL env var)",
        )
        connection_group.add_argument(
            "--migrations-dir",
            default="./migrations",
            help="Path to migrations root directory (default: %(default)s)",
        )

        # ::::: Operation mode (mutually exclusive) :::::
        operation_group = parser.add_mutually_exclusive_group()
        operation_group.add_argument(
            "--apply", action="store_true", help="Apply pending migrations (default)"
        )
        operation_group.add_argument(
            "--rollback", action="store_true", help="Rollback all applied migrations"
        )
        operation_group.add_argument(
            "--rollback-one",
            action="store_true",
            help="Rollback exactly one migration (safest leaf node)",
        )
        operation_group.add_argument(
            "--rollback-latest",
            action="store_true",
            help="Rollback the latest applied migration",
        )
        operation_group.add_argument(
            "--reload",
            action="store_true",
            help="Full reload: rollback all, then apply all",
        )

        # ::::: Execution control :::::
        execution_group = parser.add_argument_group("Execution Control")
        execution_group.add_argument(
            "--dry-run",
            action="store_true",
            help="Show execution plan without making changes",
        )
        execution_group.add_argument(
            "--no-inserters",
            action="store_true",
            help="Skip inserter migrations (schema only)",
        )

        # ::::: Domain filtering :::::
        filtering_group = parser.add_argument_group("Domain Filtering")
        filtering_group.add_argument(
            "--include",
            help="Comma-separated domains to include (e.g., 'auth,billing')",
        )
        filtering_group.add_argument(
            "--exclude", help="Comma-separated domains to exclude"
        )
        filtering_group.add_argument(
            "--domain-level",
            type=int,
            default=DEFAULT_DOMAIN_LEVEL,
            help="Directory hierarchy level for domain filtering (default: %(default)s)",
        )

        # ::::: Output and visualization :::::
        output_group = parser.add_argument_group("Output and Visualization")
        output_group.add_argument(
            "--show-structure",
            action="store_true",
            help="Display detailed migration structure analysis",
        )
        output_group.add_argument(
            "--show-graph",
            action="store_true",
            help="Display dependency graph visualization",
        )
        output_group.add_argument(
            "--graph-out", help="Write dependency graph to file (Mermaid format)"
        )
        output_group.add_argument(
            "--json-plan-out", help="Export execution plan to JSON file"
        )

        # ::::: Logging and debugging :::::
        logging_group = parser.add_argument_group("Logging and Debugging")
        logging_group.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=1,
            help="Increase logging verbosity (use multiple times for more detail)",
        )
        logging_group.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="Reduce logging verbosity to warnings only",
        )

        # ::::: Environment :::::
        env_group = parser.add_argument_group("Environment")
        env_group.add_argument(
            "--testing", action="store_true", help="Use test database configuration"
        )
        env_group.add_argument(
            "--gw-count",
            type=int,
            default=None,
            help="Number of gateway databases to migrate (requires --testing)",
        )
        env_group.add_argument(
            "--gw-template",
            type=str,
            default=None,
            help="Template for gateway database names (default: test_{db_name}_gw{i})",
        )

        return parser

    @classmethod
    def parse_config(cls, args: argparse.Namespace) -> MigrationConfig:
        dsn = args.dsn or os.environ.get("DATABASE_URL", "")
        if not dsn:
            raise SystemExit(
                "Database connection string required. "
                "Use --dsn or set DATABASE_URL environment variable."
            )

        if args.gw_count is not None and not args.testing:
            raise SystemExit("--gw-count requires --testing flag")

        if args.gw_template is not None and args.gw_count is None:
            raise SystemExit("--gw-template requires --gw-count flag")

        if args.quiet:
            verbosity = 0
        else:
            verbosity = min(args.verbose, 2)

        include_domains: Set[str] | None = None
        if args.include:
            include_domains = set(domain.strip() for domain in args.include.split(","))

        exclude_domains: Set[str] | None = None
        if args.exclude:
            exclude_domains = set(domain.strip() for domain in args.exclude.split(","))

        migrations_root = Path(args.migrations_dir).resolve()
        if not migrations_root.is_dir():
            raise SystemExit(
                f"Migrations directory not found: {migrations_root}"
            )

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
            show_structure=args.show_structure,
            show_graph=args.show_graph,
            graph_output_file=args.graph_out,
            json_plan_output_file=args.json_plan_out,
            gw_count=args.gw_count,
            gw_template=args.gw_template,
        )

    @staticmethod
    def determine_operation_mode(args: argparse.Namespace) -> str:
        if args.rollback:
            return "rollback"
        if args.rollback_one:
            return "rollback-one"
        if args.rollback_latest:
            return "rollback-latest"
        if args.reload:
            return "reload"
        return "apply"
