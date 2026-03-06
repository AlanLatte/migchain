"""Adapter: yoyo-migrations file discovery."""

import logging
import os
from pathlib import Path
from typing import Any, List, Optional, Sequence, Set

from yoyo import read_migrations

from migchain.constants import (
    DEFAULT_DOMAIN_LEVEL,
    INIT_FILE,
    LOGGER_NAME,
    MIGRATION_FILE_EXTENSION,
)

LOGGER = logging.getLogger(LOGGER_NAME)


class YoyoDiscoveryAdapter:
    """Implements MigrationRepository port using yoyo-migrations."""

    @staticmethod
    def discover_directories(
        root: Path,
        include_domains: Optional[Set[str]] = None,
        exclude_domains: Optional[Set[str]] = None,
        domain_level: int = DEFAULT_DOMAIN_LEVEL,
    ) -> List[Path]:
        migration_dirs: Set[Path] = set()

        for dirpath, _, filenames in os.walk(root):
            current = Path(dirpath)

            try:
                relative = current.relative_to(root)
            except ValueError:  # pragma: no cover
                continue

            domain = ""
            if relative.parts and len(relative.parts) > domain_level:
                domain = relative.parts[domain_level]

            if include_domains and domain and domain not in include_domains:
                continue
            if exclude_domains and domain and domain in exclude_domains:
                continue

            py_files = [
                f
                for f in filenames
                if f.endswith(MIGRATION_FILE_EXTENSION) and f != INIT_FILE
            ]

            if py_files:
                migration_dirs.add(current)
                LOGGER.debug("[discovery] %s (%d files)", current, len(py_files))

        return sorted(migration_dirs)

    @staticmethod
    def read_migrations(paths: Sequence[Path]) -> Any:
        if not paths:
            raise SystemExit("No migration folders found")

        for path in paths:
            LOGGER.debug("[discovery] Reading: %s", path)

        return read_migrations(*(str(p) for p in paths))
