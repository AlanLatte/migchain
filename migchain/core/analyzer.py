"""Migration analysis and categorization."""

from collections import defaultdict
from pathlib import Path
from typing import Any

from yoyo.migrations import MigrationList

from migchain.core.models import MigrationStructure


class MigrationAnalyzer:
    """Analyzes migration properties and categorizes them."""

    @staticmethod
    def get_migration_domain(migration: Any, migrations_root: Path) -> str:
        path_str = str(getattr(migration, "path", ""))
        if not path_str:
            return "unknown"

        try:
            path_obj = Path(path_str)
            relative_path = path_obj.relative_to(migrations_root)
            if relative_path.parts:
                return relative_path.parts[0]
            return "root"
        except (ValueError, IndexError):
            return "external"

    @staticmethod
    def get_migration_full_path(migration: Any, migrations_root: Path) -> str:
        path_str = str(getattr(migration, "path", ""))
        if not path_str:
            return "unknown"

        try:
            path_obj = Path(path_str)
            relative_path = path_obj.relative_to(migrations_root)
            return str(relative_path.parent)
        except ValueError:
            return "external"

    @staticmethod
    def is_inserter_migration(migration: Any) -> bool:
        path_str = str(getattr(migration, "path", ""))
        if not path_str:
            return False

        path_parts = Path(path_str).parts
        return "inserters" in path_parts

    @classmethod
    def get_migration_category(cls, migration: Any) -> str:
        return "inserter" if cls.is_inserter_migration(migration) else "schema"

    @classmethod
    def analyze_migration_structure(
        cls, migrations: MigrationList, migrations_root: Path
    ) -> MigrationStructure:
        structure = MigrationStructure(
            total=len(migrations),
            by_category=defaultdict(int),
            by_domain=defaultdict(list),
            by_path=defaultdict(list),
            inserter_paths=set(),
            schema_paths=set(),
        )

        for migration in migrations:
            category = cls.get_migration_category(migration)
            domain = cls.get_migration_domain(migration, migrations_root)

            structure.by_category[category] += 1
            structure.by_domain[domain].append(migration.id)

            path_str = str(getattr(migration, "path", ""))
            if path_str:
                try:
                    path_obj = Path(path_str)
                    relative_path = path_obj.relative_to(migrations_root)
                    parent_dir = str(relative_path.parent)
                    structure.by_path[parent_dir].append(migration.id)

                    if category == "inserter":
                        structure.inserter_paths.add(parent_dir)
                    else:
                        structure.schema_paths.add(parent_dir)
                except ValueError:
                    structure.by_path["external"].append(migration.id)

        return structure
