"""PostgresBatchTracker.record_apply -- persisting apply operations.

- records single migration
- records multiple migrations in one batch
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import TABLE, PostgresBatchTracker


@pytest.mark.integration
class TestRecordsMigrations:
    """Protects the INSERT contract for apply operation persistence."""

    def test_records_single(self, clean_batch_table: psycopg.Connection):
        """Protects against single migration not being persisted."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, ["migration_001"])

        with clean_batch_table.cursor() as cur:
            cur.execute(
                f"SELECT batch_number, migration_id, operation FROM {TABLE}",
            )
            rows = cur.fetchall()

        assert len(rows) == 1
        assert rows[0][0] == 1
        assert rows[0][1] == "migration_001"
        assert rows[0][2] == "apply"

    def test_records_multiple(self, clean_batch_table: psycopg.Connection):
        """Protects against batch INSERT dropping migrations."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        ids = ["m_1", "m_2", "m_3"]
        tracker.record_apply(clean_batch_table, 1, ids)

        with clean_batch_table.cursor() as cur:
            cur.execute(f"SELECT migration_id FROM {TABLE}")
            rows = cur.fetchall()

        assert len(rows) == 3
