"""Database backend management."""

import logging
import re
from typing import Optional

from yoyo import get_backend

from migchain.types import YoyoBackend

LOGGER = logging.getLogger("migchain")


class BackendManager:
    """Manages database backend connections."""

    @staticmethod
    def get_base_database_name(dsn: str) -> str:
        """Extract database name from DSN."""
        match = re.search(r"/([\w-]+)(\?|$)", dsn)
        if match:
            return match.group(1)
        raise ValueError("Cannot extract database name from DSN")

    @staticmethod
    def _ensure_yoyo_tables(backend: YoyoBackend) -> None:
        """Ensure yoyo internal tables exist."""
        try:
            backend.execute("SELECT 1 FROM yoyo_lock LIMIT 1")
        except backend.DatabaseError:
            LOGGER.info("[backend] Creating yoyo_lock table")
            backend.execute(backend.format_sql(backend.create_lock_table_sql))
            backend.connection.commit()

    @staticmethod
    def create_backend(
        dsn: str,
        testing: bool = False,
        database_name_override: Optional[str] = None,
    ) -> YoyoBackend:
        connection_dsn = dsn.replace("postgresql://", "postgresql+psycopg://")

        if database_name_override:
            connection_dsn = re.sub(
                r"/([\w-]+)(\?|$)",
                lambda m: f"/{database_name_override}{m.group(2)}",
                connection_dsn,
            )
        elif testing:
            connection_dsn = re.sub(
                r"/([\w-]+)(\?|$)",
                lambda m: f"/test_{m.group(1)}{m.group(2)}",
                connection_dsn,
            )

        masked_dsn = re.sub(r":[^@]+@", ":****@", connection_dsn)
        LOGGER.info("[backend] Connecting to: %s", masked_dsn)

        backend = get_backend(connection_dsn)
        BackendManager._ensure_yoyo_tables(backend)

        return backend
