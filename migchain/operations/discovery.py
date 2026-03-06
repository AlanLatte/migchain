"""Migration discovery and loading."""

import logging
import os
from pathlib import Path
from typing import List, Optional, Sequence, Set

from yoyo import read_migrations
from yoyo.migrations import MigrationList

from migchain.constants import (
    DEFAULT_DOMAIN_LEVEL,
    INIT_FILE,
    LOGGER_NAME,
    MIGRATION_FILE_EXTENSION,
)

LOGGER = logging.getLogger(LOGGER_NAME)


class MigrationDiscovery:
    """Discovers migration files and directories."""

    @staticmethod
    def find_migration_directories(
        root: Path,
        include_domains: Optional[Set[str]] = None,
        exclude_domains: Optional[Set[str]] = None,
        domain_level: int = DEFAULT_DOMAIN_LEVEL,
    ) -> List[Path]:
        migration_dirs: Set[Path] = set()

        for dirpath, dirnames, filenames in os.walk(root):
            current_path = Path(dirpath)

            try:
                relative_path = current_path.relative_to(root)
            except ValueError:
                continue

            if relative_path.parts and len(relative_path.parts) > domain_level:
                domain = relative_path.parts[domain_level]
            else:
                domain = ""

            if include_domains and domain and domain not in include_domains:
                continue
            if exclude_domains and domain and domain in exclude_domains:
                continue

            python_files = [
                filename
                for filename in filenames
                if filename.endswith(MIGRATION_FILE_EXTENSION) and filename != INIT_FILE
            ]

            if python_files:
                migration_dirs.add(current_path)
                LOGGER.debug(
                    "[discovery] Found migration directory: %s (%d files)",
                    current_path,
                    len(python_files),
                )

        return sorted(migration_dirs)

    @staticmethod
    def read_all_migrations(paths: Sequence[Path]) -> MigrationList:
        if not paths:
            raise SystemExit("No migration folders found")

        for path in paths:
            LOGGER.info("[migchain] Reading from source: %s", path)

        return read_migrations(*(str(path) for path in paths))
