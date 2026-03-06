"""Application service — main orchestrator using ports."""

import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from migchain.application.config import MigrationConfig, extract_database_name
from migchain.constants import CONFIRM_MESSAGES
from migchain.domain.analyzer import MigrationAnalyzer
from migchain.domain.dependency import DependencyResolver
from migchain.domain.graph import GraphVisualizer
from migchain.domain.models import MigrationPlan
from migchain.domain.optimizer import GraphOptimizer
from migchain.domain.planner import MigrationPlanner
from migchain.domain.ports import (
    BatchStorage,
    MigrationBackend,
    MigrationFileWriter,
    MigrationRepository,
    Presenter,
    SchemaComparator,
)
from migchain.domain.scaffolder import MigrationScaffolder


class MigrationService:
    """Orchestrates the migration workflow through ports."""

    def __init__(
        self,
        config: MigrationConfig,
        repository: MigrationRepository,
        backend: MigrationBackend,
        batch_storage: BatchStorage,
        *,
        presenter: Presenter,
        schema_comparator: Optional["SchemaComparator"] = None,
        migration_writer: Optional["MigrationFileWriter"] = None,
    ) -> None:
        self._config = config
        self._repository = repository
        self._backend = backend
        self._batch_storage = batch_storage
        self._presenter = presenter
        self._schema_comparator = schema_comparator
        self._migration_writer = migration_writer
        self._migrations: Any = None
        self._dependencies: Optional[Dict[str, Set[str]]] = None

    # ::::: Public API :::::

    def run(self, operation_mode: str) -> None:
        try:
            self._presenter.setup(2 if self._config.verbose else 1)

            if operation_mode == "new":
                self._scaffold()
                return

            self._discover_and_load()
            self._build_dependency_graph()

            if operation_mode in CONFIRM_MESSAGES and not self._config.auto_confirm:
                if not self._presenter.confirm(CONFIRM_MESSAGES[operation_mode]):
                    self._presenter.info("Operation cancelled")
                    return

            self._generate_graph_outputs()

            if operation_mode == "optimize":
                self._optimize()
                return

            if self._config.dry_run:
                self._dry_run(operation_mode)
                return

            targets = self._get_database_targets()

            for idx, db_override in enumerate(targets, 1):
                if len(targets) > 1:
                    label = db_override or "master (test_*)"
                    self._presenter.info(
                        f"Processing database {idx}/{len(targets)}: {label}",
                    )

                self._backend.connect(
                    self._config.dsn,
                    self._config.testing,
                    db_override,
                )
                self._execute(operation_mode)

        except KeyboardInterrupt:
            self._presenter.warning("Operation interrupted by user")
            raise SystemExit(1) from None
        except Exception as exc:
            self._presenter.error(str(exc))
            raise SystemExit(1) from None

    # ::::: Discovery :::::
    def _discover_and_load(self) -> None:
        paths = self._repository.discover_directories(
            self._config.migrations_root,
            self._config.include_domains,
            self._config.exclude_domains,
            self._config.domain_level,
        )
        if not paths:
            raise SystemExit(
                f"No migration folders found under {self._config.migrations_root}",
            )

        self._presenter.info(f"Discovered {len(paths)} migration folder(s)")
        self._migrations = self._repository.read_migrations(paths)

        if self._config.verbose or self._config.show_structure:
            structure = MigrationAnalyzer.analyze_structure(
                self._migrations,
                self._config.migrations_root,
            )
            self._presenter.show_structure(structure)

    def _build_dependency_graph(self) -> None:
        self._dependencies, _ = DependencyResolver.build_graph(self._migrations)
        DependencyResolver.topological_sort(self._dependencies)
        self._presenter.debug("Dependency graph validated")

    # ::::: Database targets :::::

    def _get_database_targets(self) -> List[Optional[str]]:
        if not self._config.gw_count or not self._config.testing:
            return [None]

        base = extract_database_name(self._config.dsn)
        template = self._config.gw_template or f"test_{base}__gw{{i}}"
        targets: List[Optional[str]] = [None]
        for i in range(1, self._config.gw_count + 1):
            targets.append(template.format(i=i))
        return targets

    # ::::: Execution dispatch :::::
    def _execute(self, operation_mode: str) -> None:
        dispatch = {
            "apply": self._apply,
            "rollback": self._rollback_all,
            "rollback-one": self._rollback_one,
            "rollback-latest": self._rollback_latest,
            "reload": self._reload,
        }
        handler = dispatch.get(operation_mode, self._apply)
        handler()

    # ::::: Apply :::::
    def _apply(self) -> None:
        pending = self._backend.pending(self._migrations)

        if not self._config.run_inserters:
            pending = MigrationPlanner.filter_without_inserters(pending, pending)
            self._presenter.info("Inserters skipped by configuration")

        plan = MigrationPlanner.create_plan(pending)
        self._presenter.show_plan(plan, "apply", self._config.migrations_root)

        if plan.total_count == 0:
            return

        self._batch_storage.ensure_ready(self._backend.connection)
        batch_number = self._batch_storage.next_batch_number(
            self._backend.connection,
        )

        self._execute_migrations(plan.all_migrations, "apply", "apply")

        self._batch_storage.record_apply(
            self._backend.connection,
            batch_number,
            [m.id for m in plan.all_migrations],
        )
        self._presenter.show_result(
            f"Applied {plan.total_count} migration(s) · Batch #{batch_number}",
        )

    # ::::: Rollback all :::::
    def _rollback_all(self) -> None:
        applied = self._backend.applied(self._migrations)
        plan = MigrationPlanner.create_plan(applied)
        self._presenter.show_plan(plan, "rollback", self._config.migrations_root)
        self._execute_migrations(plan.all_migrations, "rollback", "rollback")

    # ::::: Rollback one :::::
    def _rollback_one(self) -> None:
        applied = self._backend.applied(self._migrations)
        if not applied:
            self._presenter.info("Nothing to rollback")
            return

        candidate = MigrationPlanner.find_rollback_candidate(
            applied,
            self._dependencies or {},
            list(self._migrations),
        )
        if candidate is None:  # pragma: no cover
            self._presenter.info("No rollback candidate found")
            return

        plan = MigrationPlanner.create_plan([candidate])
        self._presenter.show_plan(plan, "rollback-one", self._config.migrations_root)
        self._execute_migrations([candidate], "rollback", "rollback-one")

    # ::::: Rollback latest batch :::::
    def _rollback_latest(self) -> None:
        with self._backend.acquire_lock():
            pass

        self._batch_storage.ensure_ready(self._backend.connection)
        latest = self._batch_storage.latest_batch(self._backend.connection)

        if latest is None:
            self._presenter.info("No tracked batches found")
            return

        batch_number, migration_ids = latest

        if not migration_ids:
            self._presenter.info(
                f"Batch #{batch_number} is empty or already rolled back",
            )
            return

        migrations_by_id = {m.id: m for m in self._migrations}
        to_rollback = []
        for mid in migration_ids:
            if mid in migrations_by_id:
                to_rollback.append(migrations_by_id[mid])
            else:
                self._presenter.warning(
                    f"Migration {mid} from batch #{batch_number} not found",
                )

        if not to_rollback:
            return

        to_rollback.reverse()

        plan = MigrationPlanner.create_plan(to_rollback)
        self._presenter.show_plan(plan, "rollback-latest", self._config.migrations_root)
        self._presenter.info(f"Rolling back batch #{batch_number}")

        self._execute_migrations(to_rollback, "rollback", "rollback-latest")

        self._batch_storage.record_rollback(
            self._backend.connection,
            batch_number,
            [m.id for m in to_rollback],
        )

    # ::::: Reload :::::
    def _reload(self) -> None:
        self._presenter.info("Starting rollback phase")
        self._rollback_all()
        self._presenter.info("Starting apply phase")
        self._apply()

    # ::::: Dry run :::::
    def _dry_run(self, operation_mode: str) -> None:
        is_rollback = operation_mode in (
            "rollback",
            "rollback-one",
            "rollback-latest",
        )
        mode = "rollback" if is_rollback else "apply"

        plan = MigrationPlanner.create_plan(list(self._migrations))
        self._presenter.show_plan(plan, f"dry-run:{mode}", self._config.migrations_root)

        if self._config.json_plan_output_file:
            json_data = self._export_plan_json(plan)
            Path(self._config.json_plan_output_file).write_text(
                json.dumps(json_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self._presenter.info(
                f"Plan written to {self._config.json_plan_output_file}",
            )

    # ::::: Low-level execution :::::
    def _execute_migrations(
        self,
        migrations: List[Any],
        operation: str,
        tag: str,
    ) -> None:
        if not migrations:
            self._presenter.info(f"[{tag}] Nothing to do")
            return

        self._presenter.start_execution(len(migrations), tag)

        with self._backend.acquire_lock():
            for migration in migrations:
                start = time.perf_counter()
                self._presenter.on_migration_start(migration.id, tag)

                try:
                    if operation == "apply":
                        self._backend.apply_one(migration)
                    else:
                        self._backend.rollback_one(migration)

                    duration = time.perf_counter() - start
                    self._presenter.on_migration_success(
                        migration.id,
                        tag,
                        duration,
                    )
                except Exception:
                    self._presenter.on_migration_fail(migration.id, tag)
                    self._presenter.finish_execution()
                    raise

        self._presenter.finish_execution()

    # ::::: Graph output :::::
    def _generate_graph_outputs(self) -> None:
        if not (self._config.show_graph or self._config.graph_output_file):
            return

        if self._migrations is None or self._dependencies is None:  # pragma: no cover
            self._presenter.warning("Cannot generate graph without migrations")
            return

        migrations_by_id = {m.id: m for m in self._migrations}
        content = GraphVisualizer.generate_mermaid(
            self._dependencies,
            migrations_by_id,
            self._config.migrations_root,
        )

        if self._config.graph_output_file:
            Path(self._config.graph_output_file).write_text(
                content,
                encoding="utf-8",
            )
            self._presenter.info(
                f"Graph written to {self._config.graph_output_file}",
            )
        else:
            self._presenter.show_graph(content)

    # ::::: Optimize :::::
    def _optimize(self) -> None:
        if self._schema_comparator is None or self._migration_writer is None:
            raise SystemExit(
                "Optimization requires extra dependencies. "
                "Install with: uv add migchain[full]",
            )

        if self._dependencies is None:  # pragma: no cover
            raise SystemExit("No dependency graph available")

        result = GraphOptimizer.transitive_reduction(self._dependencies)
        self._presenter.show_redundant_edges(result)

        if not result.redundant_edges:
            self._presenter.info("Dependency graph is already minimal")
            return

        migration_id_to_path = {
            m.id: Path(str(getattr(m, "path", ""))) for m in self._migrations
        }

        original_paths = self._repository.discover_directories(
            self._config.migrations_root,
            self._config.include_domains,
            self._config.exclude_domains,
            self._config.domain_level,
        )

        self._presenter.info("Preparing optimized migration copies...")
        temp_root = self._migration_writer.prepare_temp_copies(
            self._config.migrations_root,
            result.reduced_dependencies,
            migration_id_to_path,
        )

        optimized_paths = self._repository.discover_directories(
            temp_root,
            self._config.include_domains,
            self._config.exclude_domains,
            self._config.domain_level,
        )

        self._presenter.info("Verifying schema consistency via testcontainers...")
        verification = self._schema_comparator.verify(
            original_paths,
            optimized_paths,
        )
        self._presenter.show_verification_result(verification)

        shutil.rmtree(temp_root, ignore_errors=True)

        if not verification.is_safe:
            raise SystemExit(
                "Schema mismatch detected — optimization is NOT safe",
            )

        if not self._config.auto_confirm:
            if not self._presenter.confirm(
                "Apply optimization to migration files?",
            ):
                self._presenter.info("Optimization cancelled")
                return

        only_changed = {
            mid: deps
            for mid, deps in result.reduced_dependencies.items()
            if self._dependencies.get(mid) != deps
        }
        modified = self._migration_writer.apply_to_source(
            migration_id_to_path,
            only_changed,
        )
        removed = result.original_edge_count - result.reduced_edge_count
        self._presenter.info(
            f"Optimization complete: "
            f"{removed} redundant edge(s) removed, "
            f"{len(modified)} file(s) updated, "
            f"edges {result.original_edge_count} -> {result.reduced_edge_count}",
        )

    # ::::: Scaffolding :::::
    def _scaffold(self) -> None:
        existing_domains = MigrationScaffolder.discover_domains(
            self._config.migrations_root,
        )
        request = self._presenter.prompt_scaffold(existing_domains)
        result = MigrationScaffolder.scaffold(
            self._config.migrations_root,
            request,
        )
        self._presenter.info(f"Created {result.file_path}")

    # ::::: JSON export :::::
    def _export_plan_json(self, plan: MigrationPlan) -> list[dict[str, Any]]:
        result = []
        for m in plan.all_migrations:
            result.append(
                {
                    "id": m.id,
                    "path": str(getattr(m, "path", "")),
                    "domain": MigrationAnalyzer.get_migration_domain(
                        m,
                        self._config.migrations_root,
                    ),
                    "category": MigrationAnalyzer.get_migration_category(m),
                    "depends": sorted(
                        DependencyResolver.extract_dependency_ids(
                            getattr(m, "depends", None),
                        ),
                    ),
                },
            )
        return result
