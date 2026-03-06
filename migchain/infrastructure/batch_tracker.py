"""Adapter: PostgreSQL batch tracking."""

import logging
from typing import Any, List, Optional, Tuple

from psycopg import Error as _DatabaseError

from migchain.constants import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

TABLE = "public._yoyo_migration_batches"


class PostgresBatchTracker:
    """Implements BatchStorage port using PostgreSQL."""

    @staticmethod
    def ensure_ready(connection: Any) -> None:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TABLE} (
                        id SERIAL PRIMARY KEY,
                        batch_number INTEGER NOT NULL,
                        migration_id VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        operation VARCHAR(20) NOT NULL,
                        CONSTRAINT chk_operation
                            CHECK (operation IN ('apply', 'rollback'))
                    )
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_batch_number
                        ON {TABLE}(batch_number)
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_migration_id
                        ON {TABLE}(migration_id)
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_applied_at
                        ON {TABLE}(applied_at DESC)
                """)
                connection.commit()
            LOGGER.debug("[batch-tracker] Table %s is ready", TABLE)
        except _DatabaseError as exc:
            LOGGER.warning(
                "[batch-tracker] Could not ensure table: %s",
                exc,
            )
            try:
                connection.rollback()
            except _DatabaseError:
                pass

    @staticmethod
    def next_batch_number(connection: Any) -> int:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT COALESCE(MAX(batch_number), 0) + 1
                    FROM {TABLE}
                    WHERE operation = 'apply'
                """)
                result = cursor.fetchone()
                return result[0] if result else 1
        except _DatabaseError as exc:
            LOGGER.warning(
                "[batch-tracker] Could not get batch number: %s. Using 1.",
                exc,
            )
            return 1

    def record_apply(
        self,
        connection: Any,
        batch: int,
        ids: List[str],
    ) -> None:
        if not ids:
            return
        self._record(connection, batch, ids, "apply")

    def record_rollback(
        self,
        connection: Any,
        batch: int,
        ids: List[str],
    ) -> None:
        if not ids:
            return
        self._record(connection, batch, ids, "rollback")

    @staticmethod
    def latest_batch(
        connection: Any,
    ) -> Optional[Tuple[int, List[str]]]:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    WITH latest_batch AS (
                        SELECT batch_number
                        FROM {TABLE}
                        WHERE operation = 'apply'
                        GROUP BY batch_number
                        ORDER BY batch_number DESC
                        LIMIT 1
                    ),
                    batch_migrations AS (
                        SELECT DISTINCT migration_id
                        FROM {TABLE}
                        WHERE batch_number = (
                            SELECT batch_number FROM latest_batch
                        )
                        AND operation = 'apply'
                    ),
                    rolled_back AS (
                        SELECT DISTINCT migration_id
                        FROM {TABLE}
                        WHERE batch_number = (
                            SELECT batch_number FROM latest_batch
                        )
                        AND operation = 'rollback'
                    )
                    SELECT
                        (SELECT batch_number FROM latest_batch),
                        array_agg(bm.migration_id)
                    FROM batch_migrations bm
                    LEFT JOIN rolled_back rb
                        ON bm.migration_id = rb.migration_id
                    WHERE rb.migration_id IS NULL
                    GROUP BY batch_number
                """)
                result = cursor.fetchone()
                if result and result[0] is not None:
                    return (result[0], result[1] or [])
                return None
        except _DatabaseError as exc:
            LOGGER.warning(
                "[batch-tracker] Could not get latest batch: %s",
                exc,
            )
            return None

    @staticmethod
    def _record(
        connection: Any,
        batch: int,
        ids: List[str],
        operation: str,
    ) -> None:
        try:
            with connection.cursor() as cursor:
                values = ", ".join(
                    f"({batch}, '{mid}', CURRENT_TIMESTAMP, '{operation}')"
                    for mid in ids
                )
                cursor.execute(f"""
                    INSERT INTO {TABLE}
                        (batch_number, migration_id, applied_at, operation)
                    VALUES {values}
                """)
                connection.commit()
            LOGGER.debug(
                "[batch-tracker] Recorded %s batch #%d (%d migrations)",
                operation,
                batch,
                len(ids),
            )
        except _DatabaseError as exc:
            LOGGER.warning(
                "[batch-tracker] Could not record %s: %s",
                operation,
                exc,
            )
