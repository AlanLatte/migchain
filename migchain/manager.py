"""Main migration management orchestrator."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from yoyo.migrations import MigrationList

from migchain.constants import LOGGER_NAME
from migchain.core.analyzer import MigrationAnalyzer
from migchain.core.config import MigrationConfig
from migchain.core.dependency import DependencyAnalyzer
from migchain.core.graph import GraphGenerator
from migchain.operations.backend import BackendManager
from migchain.operations.discovery import MigrationDiscovery
from migchain.operations.executor import MigrationExecutor
from migchain.operations.planner import MigrationPlanner
from migchain.reporting.logger import LoggingManager
from migchain.reporting.report import ReportGenerator
from migchain.types import YoyoBackend

LOGGER = logging.getLogger(LOGGER_NAME)


class MigrationManager:
    """Main migration management orchestrator."""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.backend: Optional[YoyoBackend] = None
        self.migrations: Optional[MigrationList] = None
        self.dependencies: Optional[Dict[str, Set[str]]] = None

    def setup_environment(self) -> None:
        """Set up the execution environment."""
        verbosity = 2 if self.config.verbose else 1
        LoggingManager.setup_logging(verbosity)

    def discover_and_load_migrations(self) -> None:
        """Discover and load all relevant migrations."""
        migrations_root = self.config.migrations_root

        migration_paths = MigrationDiscovery.find_migration_directories(
            migrations_root,
            include_domains=self.config.include_domains,
            exclude_domains=self.config.exclude_domains,
            domain_level=self.config.domain_level,
        )

        if not migration_paths:
            raise SystemExit(
                f"No migration folders found under {migrations_root}"
            )

        LOGGER.info(
            "[migchain] Discovered %d migration folder(s)", len(migration_paths)
        )

        self.migrations = MigrationDiscovery.read_all_migrations(migration_paths)

        if self.config.verbose or self.config.show_structure:
            structure = MigrationAnalyzer.analyze_migration_structure(
                self.migrations, migrations_root
            )
            ReportGenerator.log_migration_structure(structure)

    def build_dependency_graph(self) -> None:
        """Build and validate the dependency graph."""
        if self.migrations is None:
            raise ValueError(
                "Migrations must be loaded before building dependency graph"
            )

        self.dependencies, _ = DependencyAnalyzer.build_dependency_graph(
            self.migrations
        )

        DependencyAnalyzer.topological_sort(self.dependencies)

        LOGGER.debug("[graph] Dependency graph validated successfully")

    def get_database_targets(self) -> List[Optional[str]]:
        if not self.config.gw_count or not self.config.testing:
            return [None]

        base_db_name = BackendManager.get_base_database_name(self.config.dsn)

        if self.config.gw_template:
            template = self.config.gw_template
        else:
            template = f"test_{base_db_name}__gw{{i}}"

        targets: List[Optional[str]] = [None]

        for i in range(1, self.config.gw_count + 1):
            db_name = template.format(i=i)
            targets.append(db_name)

        return targets

    def create_backend(self, database_name_override: Optional[str] = None) -> None:
        """Create database backend connection."""
        self.backend = BackendManager.create_backend(
            dsn=self.config.dsn,
            testing=self.config.testing,
            database_name_override=database_name_override,
        )
        LOGGER.debug("[backend] Database connection established")

    def generate_outputs(self) -> None:
        """Generate requested output files and visualizations."""
        if not (self.config.show_graph or self.config.graph_output_file):
            return

        if self.migrations is None or self.dependencies is None:
            LOGGER.warning("[output] Cannot generate graph without loaded migrations")
            return

        migrations_by_id = {migration.id: migration for migration in self.migrations}
        graph_content = GraphGenerator.generate_mermaid_graph(
            self.dependencies, migrations_by_id, self.config.migrations_root
        )

        if self.config.graph_output_file:
            Path(self.config.graph_output_file).write_text(
                graph_content, encoding="utf-8"
            )
            LOGGER.info(
                "[graph] Mermaid graph written to %s", self.config.graph_output_file
            )
        else:
            print(graph_content)

    def execute_dry_run(self, operation_mode: str) -> None:
        if self.backend is None or self.migrations is None:
            raise ValueError("Backend and migrations must be initialized")

        mode = (
            "rollback"
            if operation_mode in ("rollback", "rollback-one", "rollback-latest")
            else "apply"
        )
        plan = MigrationPlanner.create_execution_plan(
            self.backend, self.migrations, mode
        )
        LOGGER.info("[dry-run:%s] %d migration(s) planned", mode, plan.total_count)
        for i, migration in enumerate(plan.all_migrations, 1):
            LOGGER.info("  %3d. %s", i, migration.id)

        if mode == "apply":
            if plan.schema_count > 0:
                LOGGER.info(
                    "[dry-run:apply:schema] %d migration(s)", plan.schema_count
                )
                for i, migration in enumerate(plan.schema_migrations, 1):
                    LOGGER.info("  %3d. %s", i, migration.id)

            if plan.inserter_count > 0 and self.config.run_inserters:
                LOGGER.info(
                    "[dry-run:apply:inserters] %d migration(s)", plan.inserter_count
                )
                for i, migration in enumerate(plan.inserter_migrations, 1):
                    LOGGER.info("  %3d. %s", i, migration.id)

        if self.config.json_plan_output_file:
            migrations_by_id = {
                migration.id: migration for migration in self.migrations
            }
            json_plan = ReportGenerator.export_plan_as_json(
                plan.all_migrations, migrations_by_id, self.config.migrations_root
            )

            Path(self.config.json_plan_output_file).write_text(
                json.dumps(json_plan, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            LOGGER.info(
                "[dry-run] Execution plan written to %s",
                self.config.json_plan_output_file,
            )

    def execute_operation(self, operation_mode: str) -> None:
        if self.backend is None or self.migrations is None:
            raise ValueError("Backend and migrations must be initialized")

        if operation_mode == "rollback":
            MigrationExecutor.execute_rollback_all(self.backend, self.migrations)
        elif operation_mode == "rollback-one":
            if self.dependencies is None:
                raise ValueError("Dependencies must be built for rollback-one")
            MigrationExecutor.execute_rollback_one(
                self.backend, self.migrations, self.dependencies
            )
        elif operation_mode == "rollback-latest":
            MigrationExecutor.execute_rollback_latest(self.backend, self.migrations)
        elif operation_mode == "reload":
            MigrationExecutor.execute_reload(
                self.backend, self.migrations, self.config.run_inserters
            )
        else:
            MigrationExecutor.execute_phased_application(
                self.backend, self.migrations, self.config.run_inserters
            )

    def run(self, operation_mode: str) -> None:
        try:
            self.setup_environment()
            self.discover_and_load_migrations()
            self.build_dependency_graph()

            database_targets = self.get_database_targets()
            total_targets = len(database_targets)

            for idx, db_name_override in enumerate(database_targets, 1):
                if total_targets > 1:
                    target_label = db_name_override or "master (test_*)"
                    LOGGER.info(
                        "[migchain] Processing database %d/%d: %s",
                        idx,
                        total_targets,
                        target_label,
                    )

                self.create_backend(database_name_override=db_name_override)
                self.generate_outputs()

                if self.config.dry_run:
                    self.execute_dry_run(operation_mode)
                else:
                    self.execute_operation(operation_mode)

        except KeyboardInterrupt:
            LOGGER.warning("[migchain] Operation interrupted by user")
            raise SystemExit(1) from None
        except Exception as error:
            LOGGER.error("[migchain] Operation failed: %s", error)
            if self.config.verbose:
                LOGGER.exception("[migchain] Detailed error information:")
            raise SystemExit(1) from None
