"""PostgresBatchTracker.record_rollback -- persisting rollback.

- records rollback operation
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import TABLE, PostgresBatchTracker


@pytest.mark.integration
class TestRecordsRollbackOp:
    """Protects the INSERT contract for rollback operation persistence."""

    def test_records_rollback(self, clean_batch_table: psycopg.Connection):
        """Protects against rollback operation not being stored with correct type."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_rollback(clean_batch_table, 1, ["migration_001"])

        with clean_batch_table.cursor() as cur:
            cur.execute(
                f"SELECT batch_number, migration_id, operation FROM {TABLE}",
            )
            rows = cur.fetchall()

        assert len(rows) == 1
        assert rows[0][2] == "rollback"
