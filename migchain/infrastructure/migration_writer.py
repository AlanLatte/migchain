"""Adapter: migration file dependency rewriter."""

import logging
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set

from migchain.constants import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

DEPENDS_PATTERN = re.compile(
    r"((?:__)?depends(?:__)?)\s*=\s*[\[{](.*?)[\]}]",
    re.DOTALL,
)


class FilesystemMigrationWriter:
    """Implements MigrationFileWriter port using filesystem operations."""

    def prepare_temp_copies(
        self,
        migrations_root: Path,
        optimized_dependencies: Dict[str, Set[str]],
        migration_id_to_path: Dict[str, Path],
    ) -> Path:
        """Copy migration tree to temp dir with optimized depends."""
        temp_root = migrations_root.parent / "_migchain_optimized"
        if temp_root.exists():
            shutil.rmtree(temp_root)
        shutil.copytree(migrations_root, temp_root)

        for migration_id, new_deps in optimized_dependencies.items():
            original_path = migration_id_to_path.get(migration_id)
            if original_path is None:
                continue

            try:
                relative = original_path.relative_to(migrations_root)
            except ValueError:
                continue

            temp_path = temp_root / relative
            if temp_path.exists():
                self._rewrite_depends(temp_path, new_deps)

        LOGGER.debug(
            "[writer] Prepared optimized copies at %s",
            temp_root,
        )
        return temp_root

    def apply_to_source(
        self,
        migration_id_to_path: Dict[str, Path],
        optimized_dependencies: Dict[str, Set[str]],
    ) -> List[str]:
        """Rewrite depends in the original migration files."""
        modified: List[str] = []
        for migration_id, new_deps in optimized_dependencies.items():
            path = migration_id_to_path.get(migration_id)
            if path is None or not path.exists():
                continue
            self._rewrite_depends(path, new_deps)
            modified.append(str(path))
            LOGGER.debug(
                "[writer] Updated %s: depends = %s",
                path.name,
                sorted(new_deps),
            )
        return modified

    @staticmethod
    def _rewrite_depends(path: Path, new_deps: Set[str]) -> None:
        """Replace the depends assignment in a migration file."""
        content = path.read_text(encoding="utf-8")
        formatted = ", ".join(f'"{d}"' for d in sorted(new_deps))

        def _replacer(match: re.Match[str]) -> str:
            var_name = match.group(0).split("=")[0].rstrip()
            if "{" in match.group(0):
                return f"{var_name} = {{{formatted}}}"
            return f"{var_name} = [{formatted}]"

        new_content = DEPENDS_PATTERN.sub(_replacer, content)
        path.write_text(new_content, encoding="utf-8")
