"""Batch tracking for migration operations."""

import logging
from typing import List, Optional

from migchain.constants import LOGGER_NAME
from migchain.types import YoyoBackend

LOGGER = logging.getLogger(LOGGER_NAME)


class BatchTracker:
    """Tracks migration batches for rollback-latest functionality."""

    TABLE_NAME = "public._yoyo_migration_batches"

    @classmethod
    def ensure_table_exists(cls, backend: YoyoBackend) -> None:
        try:
            with backend.connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                        id SERIAL PRIMARY KEY,
                        batch_number INTEGER NOT NULL,
                        migration_id VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        operation VARCHAR(20) NOT NULL,

                        CONSTRAINT chk_operation CHECK (operation IN ('apply', 'rollback'))
                    )
                    """
                )

                cursor.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_batch_number
                        ON {cls.TABLE_NAME}(batch_number)
                    """
                )
                cursor.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_migration_id
                        ON {cls.TABLE_NAME}(migration_id)
                    """
                )
                cursor.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_applied_at
                        ON {cls.TABLE_NAME}(applied_at DESC)
                    """
                )

                backend.connection.commit()

            LOGGER.debug("[batch-tracker] Table %s is ready", cls.TABLE_NAME)

        except Exception as e:
            LOGGER.warning(
                "[batch-tracker] Could not ensure table exists: %s. "
                "Batch tracking will be disabled.",
                e,
            )
            try:
                backend.connection.rollback()
            except Exception:
                pass

    @classmethod
    def get_next_batch_number(cls, backend: YoyoBackend) -> int:
        try:
            with backend.connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT COALESCE(MAX(batch_number), 0) + 1
                    FROM {cls.TABLE_NAME}
                    WHERE operation = 'apply'
                    """
                )
                result = cursor.fetchone()
                return result[0] if result else 1
        except Exception as e:
            LOGGER.warning(
                "[batch-tracker] Could not get next batch number: %s. Using 1.", e
            )
            return 1

    @classmethod
    def record_batch_apply(
        cls, backend: YoyoBackend, batch_number: int, migration_ids: List[str]
    ) -> None:
        if not migration_ids:
            return

        try:
            with backend.connection.cursor() as cursor:
                values = [
                    f"({batch_number}, '{migration_id}', CURRENT_TIMESTAMP, 'apply')"
                    for migration_id in migration_ids
                ]

                cursor.execute(
                    f"""
                    INSERT INTO {cls.TABLE_NAME}
                        (batch_number, migration_id, applied_at, operation)
                    VALUES {', '.join(values)}
                    """
                )
                backend.connection.commit()

            LOGGER.info(
                "[batch-tracker] Recorded batch #%d with %d migration(s)",
                batch_number,
                len(migration_ids),
            )
        except Exception as e:
            LOGGER.warning(
                "[batch-tracker] Could not record batch: %s. "
                "Rollback-latest may not work correctly.",
                e,
            )

    @classmethod
    def record_batch_rollback(
        cls, backend: YoyoBackend, batch_number: int, migration_ids: List[str]
    ) -> None:
        if not migration_ids:
            return

        try:
            with backend.connection.cursor() as cursor:
                values = [
                    f"({batch_number}, '{migration_id}', CURRENT_TIMESTAMP, 'rollback')"
                    for migration_id in migration_ids
                ]

                cursor.execute(
                    f"""
                    INSERT INTO {cls.TABLE_NAME}
                        (batch_number, migration_id, applied_at, operation)
                    VALUES {', '.join(values)}
                    """
                )
                backend.connection.commit()

            LOGGER.info(
                "[batch-tracker] Recorded rollback of batch #%d with %d migration(s)",
                batch_number,
                len(migration_ids),
            )
        except Exception as e:
            LOGGER.warning("[batch-tracker] Could not record rollback: %s", e)

    @classmethod
    def get_latest_batch(cls, backend: YoyoBackend) -> Optional[tuple[int, List[str]]]:
        try:
            with backend.connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    WITH latest_batch AS (
                        SELECT batch_number
                        FROM {cls.TABLE_NAME}
                        WHERE operation = 'apply'
                        GROUP BY batch_number
                        ORDER BY batch_number DESC
                        LIMIT 1
                    ),
                    batch_migrations AS (
                        SELECT DISTINCT migration_id
                        FROM {cls.TABLE_NAME}
                        WHERE batch_number = (SELECT batch_number FROM latest_batch)
                          AND operation = 'apply'
                    ),
                    rolled_back AS (
                        SELECT DISTINCT migration_id
                        FROM {cls.TABLE_NAME}
                        WHERE batch_number = (SELECT batch_number FROM latest_batch)
                          AND operation = 'rollback'
                    )
                    SELECT
                        (SELECT batch_number FROM latest_batch) as batch_number,
                        array_agg(bm.migration_id) as migration_ids
                    FROM batch_migrations bm
                    LEFT JOIN rolled_back rb ON bm.migration_id = rb.migration_id
                    WHERE rb.migration_id IS NULL
                    GROUP BY batch_number
                    """
                )

                result = cursor.fetchone()
                if result and result[0] is not None:
                    batch_number = result[0]
                    migration_ids = result[1] if result[1] else []
                    return (batch_number, migration_ids)

                return None

        except Exception as e:
            LOGGER.warning("[batch-tracker] Could not get latest batch: %s", e)
            return None

    @classmethod
    def get_batch_info(cls, backend: YoyoBackend, batch_number: int) -> List[dict]:
        try:
            with backend.connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        migration_id,
                        applied_at,
                        operation
                    FROM {cls.TABLE_NAME}
                    WHERE batch_number = %s
                    ORDER BY applied_at
                    """,
                    (batch_number,),
                )

                rows = cursor.fetchall()
                return [
                    {
                        "migration_id": row[0],
                        "applied_at": row[1],
                        "operation": row[2],
                    }
                    for row in rows
                ]

        except Exception as e:
            LOGGER.warning("[batch-tracker] Could not get batch info: %s", e)
            return []
