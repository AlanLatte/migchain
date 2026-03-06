"""PostgresBatchTracker.latest_batch -- latest non-rolled-back batch.

- returns latest batch with migration IDs
- excludes rolled-back migrations
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import PostgresBatchTracker


@pytest.mark.integration
class TestReturnsLatestUnapplied:
    """Protects the latest-batch query against incorrect batch selection."""

    def test_returns_latest(self, clean_batch_table: psycopg.Connection):
        """Protects against returning an older batch instead of the latest."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, ["m_a"])
        tracker.record_apply(clean_batch_table, 2, ["m_b", "m_c"])

        result = tracker.latest_batch(clean_batch_table)

        assert result is not None
        batch_number, ids = result
        assert batch_number == 2
        assert sorted(ids) == ["m_b", "m_c"]

    def test_excludes_rolled_back(
        self,
        clean_batch_table: psycopg.Connection,
    ):
        """Protects against rolled-back migrations appearing in latest batch."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, ["m1", "m2"])
        tracker.record_rollback(clean_batch_table, 1, ["m1"])

        result = tracker.latest_batch(clean_batch_table)

        assert result is not None
        _, ids = result
        assert ids == ["m2"]
