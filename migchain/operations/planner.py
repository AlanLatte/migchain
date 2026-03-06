"""Migration planning strategies."""

from collections import defaultdict
from typing import Any, DefaultDict, Dict, Optional, Set

from yoyo.migrations import MigrationList

from migchain.core.analyzer import MigrationAnalyzer
from migchain.core.models import MigrationPlan
from migchain.types import YoyoBackend


class MigrationPlanner:
    """Plans migration execution strategies."""

    @staticmethod
    def create_execution_plan(
        backend: YoyoBackend, migrations: MigrationList, mode: str = "apply"
    ) -> MigrationPlan:
        if mode == "rollback":
            planned_migrations = list(backend.to_rollback(migrations))
        else:
            planned_migrations = list(backend.to_apply(migrations))

        schema_migrations = [
            migration
            for migration in planned_migrations
            if not MigrationAnalyzer.is_inserter_migration(migration)
        ]

        inserter_migrations = [
            migration
            for migration in planned_migrations
            if MigrationAnalyzer.is_inserter_migration(migration)
        ]

        return MigrationPlan(
            schema_migrations=schema_migrations,
            inserter_migrations=inserter_migrations,
            all_migrations=planned_migrations,
        )

    @staticmethod
    def find_rollback_candidate(
        backend: YoyoBackend,
        migrations: MigrationList,
        dependencies: Dict[str, Set[str]],
    ) -> Optional[Any]:
        applied_migrations = list(backend.to_rollback(migrations))
        if not applied_migrations:
            return None

        applied_ids = {migration.id for migration in applied_migrations}
        migrations_by_id = {migration.id: migration for migration in migrations}

        children: DefaultDict[str, Set[str]] = defaultdict(set)
        for child, parents in dependencies.items():
            for parent in parents:
                children[parent].add(child)

        leaf_candidates = []
        for migration_id in applied_ids:
            migration_children = children.get(migration_id, set())
            if not (migration_children & applied_ids):
                leaf_candidates.append(migration_id)

        if not leaf_candidates:
            return applied_migrations[0]

        chosen_id = max(leaf_candidates)
        return migrations_by_id[chosen_id]

    @staticmethod
    def find_latest_applied_migration(
        backend: YoyoBackend,
        migrations: MigrationList,
    ) -> Optional[Any]:
        applied_migrations = list(backend.to_rollback(migrations))
        if not applied_migrations:
            return None

        return applied_migrations[-1]
