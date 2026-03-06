"""PostgresBatchTracker.record_apply -- empty ID list.

- empty list -> no rows inserted
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import TABLE, PostgresBatchTracker


@pytest.mark.integration
class TestEmptyIds:
    """Protects the no-op contract when an empty ID list is provided."""

    def test_empty_ids_skipped(self, clean_batch_table: psycopg.Connection):
        """Protects against empty list causing SQL errors or phantom rows."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, [])

        with clean_batch_table.cursor() as cur:
            cur.execute(f"SELECT migration_id FROM {TABLE}")
            rows = cur.fetchall()

        assert len(rows) == 0
