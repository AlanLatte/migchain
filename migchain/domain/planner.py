"""Domain service: migration planning strategies."""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from migchain.domain.analyzer import MigrationAnalyzer
from migchain.domain.models import MigrationPlan


class MigrationPlanner:
    """Pure domain logic for planning migration execution."""

    @staticmethod
    def create_plan(migrations: List[Any]) -> MigrationPlan:
        schema = [
            m for m in migrations if not MigrationAnalyzer.is_inserter_migration(m)
        ]
        inserters = [
            m for m in migrations if MigrationAnalyzer.is_inserter_migration(m)
        ]
        return MigrationPlan(
            schema_migrations=schema,
            inserter_migrations=inserters,
            all_migrations=migrations,
        )

    @staticmethod
    def find_rollback_candidate(
        applied: List[Any],
        dependencies: Dict[str, Set[str]],
        all_migrations: List[Any],
    ) -> Optional[Any]:
        if not applied:
            return None

        applied_ids = {m.id for m in applied}
        migrations_by_id = {m.id: m for m in all_migrations}

        children: dict[str, Set[str]] = defaultdict(set)
        for child, parents in dependencies.items():
            for parent in parents:
                children[parent].add(child)

        leaf_candidates = [
            mid for mid in applied_ids if not (children.get(mid, set()) & applied_ids)
        ]

        if not leaf_candidates:
            return applied[0]

        chosen_id = max(leaf_candidates)
        return migrations_by_id[chosen_id]

    @staticmethod
    def filter_without_inserters(
        migrations: List[Any],
        all_pending: List[Any],
    ) -> List[Any]:
        """Filter out inserters with dependency conflict check."""
        filtered = [
            m for m in migrations if not MigrationAnalyzer.is_inserter_migration(m)
        ]

        inserter_ids = {
            m.id for m in all_pending if MigrationAnalyzer.is_inserter_migration(m)
        }

        for migration in filtered:
            depends = getattr(migration, "depends", set()) or set()
            conflicting = depends & inserter_ids
            if conflicting:
                skipped = ", ".join(sorted(conflicting))
                raise SystemExit(
                    f"Migration {migration.id} depends on inserter(s) "
                    f"that would be skipped: {skipped}. "
                    "Remove --no-inserters or adjust dependencies.",
                )

        return filtered
