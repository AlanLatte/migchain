"""PostgresBatchTracker.latest_batch -- boundary conditions.

- no batches -> None
- all rolled back -> None
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import PostgresBatchTracker


@pytest.mark.integration
class TestNoBatchesAndFullyRolledBack:
    """Protects None-return contract for empty or fully-rolled-back state."""

    def test_no_batches(self, clean_batch_table: psycopg.Connection):
        """Protects against non-None return on an empty table."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        result = tracker.latest_batch(clean_batch_table)

        assert result is None

    def test_fully_rolled_back(
        self,
        clean_batch_table: psycopg.Connection,
    ):
        """Protects against returning a batch where all migrations are rolled back."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, ["m1"])
        tracker.record_rollback(clean_batch_table, 1, ["m1"])

        result = tracker.latest_batch(clean_batch_table)

        assert result is None
