"""PostgresBatchTracker.next_batch_number -- sequential generation.

- first batch is 1
- increments after apply
- increments sequentially
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import PostgresBatchTracker


@pytest.mark.integration
class TestSequentialNumbers:
    """Protects the monotonic batch numbering contract."""

    def test_first_is_one(self, clean_batch_table: psycopg.Connection):
        """Protects against first batch number not being 1."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        result = tracker.next_batch_number(clean_batch_table)

        assert result == 1

    def test_increments_after_apply(
        self,
        clean_batch_table: psycopg.Connection,
    ):
        """Protects against batch number not advancing after record_apply."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, ["m_a"])
        result = tracker.next_batch_number(clean_batch_table)

        assert result == 2

    def test_increments_sequentially(
        self,
        clean_batch_table: psycopg.Connection,
    ):
        """Protects against non-sequential batch number gaps."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        tracker.record_apply(clean_batch_table, 1, ["m_a"])
        tracker.record_apply(clean_batch_table, 2, ["m_b"])
        result = tracker.next_batch_number(clean_batch_table)

        assert result == 3
