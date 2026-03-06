"""Report generation for migrations."""

import logging
from pathlib import Path
from typing import Any, Dict, List

from migchain.constants import LOGGER_NAME
from migchain.core.analyzer import MigrationAnalyzer
from migchain.core.dependency import DependencyAnalyzer
from migchain.core.models import MigrationStructure

LOGGER = logging.getLogger(LOGGER_NAME)


class ReportGenerator:
    """Generates various reports and outputs."""

    @staticmethod
    def log_migration_structure(structure: MigrationStructure) -> None:
        LOGGER.info("[structure] Total migrations: %d", structure.total)

        LOGGER.info("[structure] By category:")
        for category, count in structure.by_category.items():
            LOGGER.info("  - %s: %d", category, count)

        LOGGER.info("[structure] By domain:")
        for domain, migration_ids in sorted(structure.by_domain.items()):
            LOGGER.info("  - %s: %d migrations", domain, len(migration_ids))
            if LOGGER.isEnabledFor(logging.DEBUG):
                for migration_id in migration_ids:
                    LOGGER.debug("    * %s", migration_id)

        LOGGER.info("[structure] Schema directories: %d", len(structure.schema_paths))
        for path in sorted(structure.schema_paths):
            count = len(structure.by_path[path])
            LOGGER.debug("  - %s (%d migrations)", path, count)

        LOGGER.info(
            "[structure] Inserter directories: %d", len(structure.inserter_paths)
        )
        for path in sorted(structure.inserter_paths):
            count = len(structure.by_path[path])
            LOGGER.debug("  - %s (%d migrations)", path, count)

    @staticmethod
    def export_plan_as_json(
        plan_migrations: List[Any],
        migrations_by_id: Dict[str, Any],
        migrations_root: Path,
    ) -> List[Dict[str, Any]]:
        json_plan = []
        for migration in plan_migrations:
            migration_data = {
                "id": migration.id,
                "path": str(getattr(migration, "path", "")),
                "domain": MigrationAnalyzer.get_migration_domain(
                    migration, migrations_root
                ),
                "category": MigrationAnalyzer.get_migration_category(migration),
                "depends": sorted(
                    DependencyAnalyzer.extract_dependency_ids(
                        getattr(migration, "depends", None)
                    )
                ),
            }
            json_plan.append(migration_data)

        return json_plan
