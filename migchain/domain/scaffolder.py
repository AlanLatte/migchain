"""Domain: migration file scaffolding."""

import random
import string
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional


@dataclass
class ScaffoldRequest:
    """User request to create a new migration."""

    scaffold_type: str
    domain: str
    subdirectory: str = ""
    description: str = ""


@dataclass
class ScaffoldResult:
    """Result of migration scaffolding."""

    file_path: Path
    migration_id: str


class MigrationScaffolder:
    """Generates migration file scaffolds."""

    @staticmethod
    def scaffold(
        migrations_root: Path,
        request: ScaffoldRequest,
    ) -> ScaffoldResult:
        """Create a new migration file based on the request."""
        handlers = {
            "domain": MigrationScaffolder._scaffold_domain,
            "inserter": MigrationScaffolder._scaffold_inserter,
        }
        handler = handlers.get(
            request.scaffold_type,
            MigrationScaffolder._scaffold_migration,
        )
        return handler(migrations_root, request)

    @staticmethod
    def discover_domains(migrations_root: Path) -> List[str]:
        """List existing domain directories."""
        if not migrations_root.exists():
            return []
        return sorted(
            d.name
            for d in migrations_root.iterdir()
            if d.is_dir() and not d.name.startswith(("_", "."))
        )

    @staticmethod
    def discover_subdirectories(
        migrations_root: Path,
        domain: str,
    ) -> List[str]:
        """List existing subdirectories within a domain."""
        domain_dir = migrations_root / domain
        if not domain_dir.exists():
            return []
        return sorted(
            d.name
            for d in domain_dir.iterdir()
            if d.is_dir() and not d.name.startswith(("_", "."))
        )

    @staticmethod
    def _scaffold_domain(root: Path, request: ScaffoldRequest) -> ScaffoldResult:
        domain_dir = root / request.domain
        domain_dir.mkdir(parents=True, exist_ok=True)

        migration_id = MigrationScaffolder._generate_id(
            domain_dir,
            request.domain,
            "",
            "create-schema",
        )

        content = (
            f'"""Create {request.domain} schema."""\n\n'
            "from yoyo import step\n\n"
            "steps = [\n"
            "    step(\n"
            f'        "CREATE SCHEMA IF NOT EXISTS {request.domain}",\n'
            f'        "DROP SCHEMA IF EXISTS {request.domain} CASCADE",\n'
            "    ),\n"
            "]\n"
        )

        file_path = domain_dir / f"{migration_id}.py"
        file_path.write_text(content, encoding="utf-8")
        return ScaffoldResult(file_path=file_path, migration_id=migration_id)

    @staticmethod
    def _scaffold_migration(
        root: Path,
        request: ScaffoldRequest,
    ) -> ScaffoldResult:
        target_dir = root / request.domain
        if request.subdirectory:
            target_dir = target_dir / request.subdirectory
        target_dir.mkdir(parents=True, exist_ok=True)

        description = request.description or "new-migration"
        migration_id = MigrationScaffolder._generate_id(
            target_dir,
            request.domain,
            request.subdirectory,
            description,
        )

        depends = MigrationScaffolder._find_latest_migration(root / request.domain)
        depends_block = ""
        if depends:
            depends_block = f'\n__depends__ = {{"{depends}"}}\n'

        docstring = description.replace("-", " ").capitalize()
        content = (
            f'"""{docstring}."""\n\n'
            "from yoyo import step\n"
            f"{depends_block}\n"
            "steps = [\n"
            "    step(\n"
            '        """\n'
            "        \n"
            '        """,\n'
            '        """\n'
            "        \n"
            '        """,\n'
            "    ),\n"
            "]\n"
        )

        file_path = target_dir / f"{migration_id}.py"
        file_path.write_text(content, encoding="utf-8")
        return ScaffoldResult(file_path=file_path, migration_id=migration_id)

    @staticmethod
    def _scaffold_inserter(
        root: Path,
        request: ScaffoldRequest,
    ) -> ScaffoldResult:
        target_dir = root / request.domain
        if request.subdirectory:
            target_dir = target_dir / request.subdirectory
        target_dir = target_dir / "inserters"
        target_dir.mkdir(parents=True, exist_ok=True)

        description = request.description or "insert-data"
        migration_id = MigrationScaffolder._generate_id(
            target_dir,
            request.domain,
            request.subdirectory,
            description,
        )

        depends = MigrationScaffolder._find_latest_migration(root / request.domain)
        depends_block = ""
        if depends:
            depends_block = f'\n__depends__ = {{"{depends}"}}\n'

        docstring = description.replace("-", " ").capitalize()
        content = (
            f'"""{docstring}."""\n\n'
            "from yoyo import step\n"
            f"{depends_block}\n"
            "steps = [\n"
            "    step(\n"
            '        """\n'
            "        \n"
            '        """,\n'
            '        """\n'
            "        \n"
            '        """,\n'
            "    ),\n"
            "]\n"
        )

        file_path = target_dir / f"{migration_id}.py"
        file_path.write_text(content, encoding="utf-8")
        return ScaffoldResult(file_path=file_path, migration_id=migration_id)

    @staticmethod
    def _generate_id(
        target_dir: Path,
        domain: str,
        subdirectory: str,
        description: str,
    ) -> str:
        today = date.today()
        date_prefix = today.strftime("%Y%m%d")

        existing = list(target_dir.glob(f"{date_prefix}_*.py"))
        seq_str = f"{len(existing):02d}"

        suffix = "".join(random.choices(string.ascii_letters, k=5))

        parts = [domain]
        if subdirectory:
            parts.extend(subdirectory.split("/"))
        parts.extend(description.split("-"))
        name_part = "-".join(parts)

        return f"{date_prefix}_{seq_str}_{suffix}-{name_part}"

    @staticmethod
    def _find_latest_migration(domain_dir: Path) -> Optional[str]:
        """Find the latest migration ID in a domain directory tree."""
        if not domain_dir.exists():
            return None

        migrations = sorted(
            f.stem for f in domain_dir.rglob("*.py") if not f.name.startswith("_")
        )

        if not migrations:
            return None
        return migrations[-1]
