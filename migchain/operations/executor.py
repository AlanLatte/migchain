"""Migration execution operations."""

import logging
import time
from typing import Any, Dict, List, Optional, Set

from yoyo.migrations import MigrationList

from migchain.constants import LOGGER_NAME
from migchain.core.analyzer import MigrationAnalyzer
from migchain.operations.batch_tracker import BatchTracker
from migchain.operations.planner import MigrationPlanner
from migchain.types import YoyoBackend

LOGGER = logging.getLogger(LOGGER_NAME)


class MigrationExecutor:
    """Executes migration operations."""

    @staticmethod
    def _log_migration_execution(
        tag: str,
        migration_id: str,
        duration: Optional[float] = None,
        status: str = "START",
    ) -> None:
        if status == "START":
            LOGGER.info("[%s] >> %s", tag, migration_id)
        elif status == "SUCCESS":
            dur_str = f" ({duration:.3f}s)" if duration is not None else ""
            LOGGER.info("[%s] OK %s%s", tag, migration_id, dur_str)
        elif status == "FAILED":
            LOGGER.error("[%s] FAIL %s", tag, migration_id)

    @classmethod
    def execute_migrations(
        cls, backend: YoyoBackend, migrations: List[Any], operation: str, tag: str
    ) -> None:
        if not migrations:
            LOGGER.info("[%s] Nothing to do", tag)
            return

        with backend.lock():
            for migration in migrations:
                start_time = time.perf_counter()
                cls._log_migration_execution(tag, migration.id, status="START")

                LOGGER.debug(
                    "[%s] Path=%s, Dependencies=%s",
                    tag,
                    getattr(migration, "path", None),
                    getattr(migration, "depends", None),
                )

                try:
                    if operation == "apply":
                        backend.apply_migrations(MigrationList([migration]))
                    elif operation == "rollback":
                        backend.rollback_migrations(MigrationList([migration]))

                    duration = time.perf_counter() - start_time
                    cls._log_migration_execution(
                        tag, migration.id, duration, status="SUCCESS"
                    )

                except Exception:
                    cls._log_migration_execution(tag, migration.id, status="FAILED")
                    LOGGER.exception("[%s] Migration execution failed", tag)
                    raise

    @classmethod
    def execute_phased_application(
        cls,
        backend: YoyoBackend,
        migrations: MigrationList,
        run_inserters: bool = True,
    ) -> None:
        try:
            with backend.lock():
                pass
        except Exception as e:
            LOGGER.warning("[apply] Could not acquire backend lock: %s", e)
            raise

        BatchTracker.ensure_table_exists(backend)

        batch_number = BatchTracker.get_next_batch_number(backend)
        applied_migration_ids: List[str] = []

        plan = MigrationPlanner.create_execution_plan(backend, migrations, "apply")

        if not run_inserters:
            migrations_to_apply = [
                migration
                for migration in plan.all_migrations
                if not MigrationAnalyzer.is_inserter_migration(migration)
            ]

            inserter_ids = {
                m.id
                for m in plan.all_migrations
                if MigrationAnalyzer.is_inserter_migration(m)
            }

            for migration in migrations_to_apply:
                depends = getattr(migration, "depends", set()) or set()
                conflicting_deps = depends & inserter_ids
                if conflicting_deps:
                    LOGGER.error(
                        "[apply] Cannot skip inserters: migration %s depends on inserter(s): %s",
                        migration.id,
                        ", ".join(sorted(conflicting_deps)),
                    )
                    raise SystemExit(
                        f"Migration {migration.id} depends on inserter migrations that would be skipped. "
                        "Remove --no-inserters flag or adjust dependencies."
                    )

            LOGGER.info("[apply] Inserters skipped by configuration")
        else:
            migrations_to_apply = plan.all_migrations

        LOGGER.info("[apply] %d migration(s) planned", len(migrations_to_apply))
        for i, migration in enumerate(migrations_to_apply, 1):
            is_inserter = MigrationAnalyzer.is_inserter_migration(migration)
            marker = "[inserter]" if is_inserter else "[schema]  "
            LOGGER.info("  %3d. %s %s", i, marker, migration.id)

        cls.execute_migrations(backend, migrations_to_apply, "apply", "apply")

        applied_migration_ids.extend([m.id for m in migrations_to_apply])

        if applied_migration_ids:
            BatchTracker.record_batch_apply(backend, batch_number, applied_migration_ids)
            LOGGER.info(
                "[apply] Recorded batch #%d with %d total migration(s)",
                batch_number,
                len(applied_migration_ids),
            )

    @classmethod
    def execute_rollback_all(
        cls, backend: YoyoBackend, migrations: MigrationList
    ) -> None:
        plan = MigrationPlanner.create_execution_plan(backend, migrations, "rollback")

        LOGGER.info("[rollback] %d migration(s) planned", plan.total_count)
        for i, migration in enumerate(plan.all_migrations, 1):
            LOGGER.info("  %3d. %s", i, migration.id)

        cls.execute_migrations(backend, plan.all_migrations, "rollback", "rollback")

    @classmethod
    def execute_rollback_one(
        cls,
        backend: YoyoBackend,
        migrations: MigrationList,
        dependencies: Dict[str, Set[str]],
    ) -> None:
        candidate = MigrationPlanner.find_rollback_candidate(
            backend, migrations, dependencies
        )

        if candidate is None:
            LOGGER.info("[rollback-one] Nothing to do")
            return

        LOGGER.info("[rollback-one] 1 migration planned")
        LOGGER.info("    1. %s", candidate.id)

        cls.execute_migrations(backend, [candidate], "rollback", "rollback-one")

    @classmethod
    def execute_rollback_latest(
        cls,
        backend: YoyoBackend,
        migrations: MigrationList,
    ) -> None:
        try:
            with backend.lock():
                pass
        except Exception as e:
            LOGGER.warning("[rollback-latest] Could not acquire backend lock: %s", e)
            raise

        BatchTracker.ensure_table_exists(backend)

        latest_batch = BatchTracker.get_latest_batch(backend)

        if latest_batch is None:
            LOGGER.info("[rollback-latest] No tracked batches found")
            return

        batch_number, migration_ids = latest_batch

        if not migration_ids:
            LOGGER.info(
                "[rollback-latest] Batch #%d is empty or already rolled back",
                batch_number,
            )
            return

        migrations_by_id = {m.id: m for m in migrations}
        migrations_to_rollback = []

        for migration_id in migration_ids:
            if migration_id in migrations_by_id:
                migrations_to_rollback.append(migrations_by_id[migration_id])
            else:
                LOGGER.warning(
                    "[rollback-latest] Migration %s from batch #%d not found",
                    migration_id,
                    batch_number,
                )

        if not migrations_to_rollback:
            LOGGER.info("[rollback-latest] No migrations to rollback")
            return

        migrations_to_rollback.reverse()

        LOGGER.info(
            "[rollback-latest] Rolling back batch #%d with %d migration(s)",
            batch_number,
            len(migrations_to_rollback),
        )
        for i, migration in enumerate(migrations_to_rollback, 1):
            LOGGER.info("  %3d. %s", i, migration.id)

        cls.execute_migrations(
            backend, migrations_to_rollback, "rollback", "rollback-latest"
        )

        BatchTracker.record_batch_rollback(
            backend, batch_number, [m.id for m in migrations_to_rollback]
        )

    @classmethod
    def execute_reload(
        cls,
        backend: YoyoBackend,
        migrations: MigrationList,
        run_inserters: bool = True,
    ) -> None:
        LOGGER.info("[reload] Starting rollback phase")
        cls.execute_rollback_all(backend, migrations)

        LOGGER.info("[reload] Starting apply phase")
        cls.execute_phased_application(backend, migrations, run_inserters)
