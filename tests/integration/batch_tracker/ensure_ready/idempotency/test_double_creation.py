"""PostgresBatchTracker.ensure_ready -- idempotent creation.

- calling ensure_ready twice doesn't fail
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import PostgresBatchTracker


@pytest.mark.integration
class TestDoubleCreation:
    """Protects idempotency of ensure_ready against DDL crashes on re-run."""

    def test_idempotent(self, clean_batch_table: psycopg.Connection):
        """Protects against 'already exists' errors on second invocation."""
        tracker = PostgresBatchTracker()

        tracker.ensure_ready(clean_batch_table)
        tracker.ensure_ready(clean_batch_table)
