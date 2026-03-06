"""Domain service: migration analysis and categorization."""

from pathlib import Path
from typing import Any

from migchain.domain.models import DomainStats, MigrationStructure


class MigrationAnalyzer:
    """Pure domain logic for analyzing migration properties."""

    @staticmethod
    def get_migration_domain(migration: Any, migrations_root: Path) -> str:
        path_str = str(getattr(migration, "path", ""))
        if not path_str:
            return "unknown"

        try:
            relative = Path(path_str).relative_to(migrations_root)
            return relative.parts[0] if relative.parts else "root"
        except (ValueError, IndexError):
            return "external"

    @staticmethod
    def get_migration_full_path(migration: Any, migrations_root: Path) -> str:
        path_str = str(getattr(migration, "path", ""))
        if not path_str:
            return "unknown"

        try:
            return str(Path(path_str).relative_to(migrations_root).parent)
        except ValueError:
            return "external"

    @staticmethod
    def is_inserter_migration(migration: Any) -> bool:
        path_str = str(getattr(migration, "path", ""))
        if not path_str:
            return False
        return "inserters" in Path(path_str).parts

    @classmethod
    def get_migration_category(cls, migration: Any) -> str:
        return "inserter" if cls.is_inserter_migration(migration) else "schema"

    @classmethod
    def analyze_structure(
        cls,
        migrations: Any,
        migrations_root: Path,
    ) -> MigrationStructure:
        domains: dict[str, DomainStats] = {}
        schema_count = 0
        inserter_count = 0
        schema_paths: set[str] = set()
        inserter_paths: set[str] = set()

        for migration in migrations:
            category = cls.get_migration_category(migration)
            domain = cls.get_migration_domain(migration, migrations_root)

            if domain not in domains:
                domains[domain] = DomainStats()

            stats = domains[domain]
            stats.migration_ids.append(migration.id)

            if category == "inserter":
                stats.inserter_count += 1
                inserter_count += 1
            else:
                stats.schema_count += 1
                schema_count += 1

            path_str = str(getattr(migration, "path", ""))
            if path_str:
                try:
                    parent = str(
                        Path(path_str).relative_to(migrations_root).parent,
                    )
                    if category == "inserter":
                        inserter_paths.add(parent)
                    else:
                        schema_paths.add(parent)
                except ValueError:
                    pass

        return MigrationStructure(
            total=len(list(migrations)),
            schema_count=schema_count,
            inserter_count=inserter_count,
            domains=domains,
            schema_paths=schema_paths,
            inserter_paths=inserter_paths,
        )
