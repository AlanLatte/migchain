"""Adapter: yoyo-migrations database backend."""

import logging
import re
from contextlib import contextmanager
from typing import Any, Iterator, List, Optional

from yoyo import get_backend
from yoyo.migrations import MigrationList

from migchain.constants import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)


class YoyoBackendAdapter:
    """Implements MigrationBackend port using yoyo-migrations."""

    def __init__(self) -> None:
        self._backend: Any = None

    @property
    def connection(self) -> Any:
        return self._backend.connection

    def connect(
        self,
        dsn: str,
        testing: bool = False,
        database_name_override: Optional[str] = None,
    ) -> None:
        connection_dsn = dsn.replace(
            "postgresql://",
            "postgresql+psycopg://",
        )

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

        masked = re.sub(r":[^@]+@", ":****@", connection_dsn)
        LOGGER.debug("[backend] Connecting to: %s", masked)

        self._backend = get_backend(connection_dsn)
        self._ensure_yoyo_tables()

    def pending(self, migrations: Any) -> List[Any]:
        return list(self._backend.to_apply(migrations))

    def applied(self, migrations: Any) -> List[Any]:
        return list(self._backend.to_rollback(migrations))

    def apply_one(self, migration: Any) -> None:
        self._backend.apply_migrations(MigrationList([migration]))

    def rollback_one(self, migration: Any) -> None:
        self._backend.rollback_migrations(MigrationList([migration]))

    @contextmanager
    def acquire_lock(self) -> Iterator[None]:
        with self._backend.lock():
            yield

    def _ensure_yoyo_tables(self) -> None:
        try:
            self._backend.execute("SELECT 1 FROM yoyo_lock LIMIT 1")
        except self._backend.DatabaseError:  # pragma: no cover
            LOGGER.info("[backend] Creating yoyo_lock table")
            self._backend.execute(
                self._backend.format_sql(self._backend.create_lock_table_sql),
            )
            self._backend.connection.commit()
