"""PostgresBatchTracker.record_rollback -- empty IDs early return.

- empty list -> returns immediately without touching DB
"""

from unittest.mock import MagicMock

from migchain.infrastructure.batch_tracker import PostgresBatchTracker


class TestEmptyIds:
    """Protects against unnecessary DB calls when there are no IDs to record."""

    def test_empty_ids_skips_record(self):
        """Protects against INSERT being called with no migration IDs."""
        conn = MagicMock()
        tracker = PostgresBatchTracker()
        tracker.record_rollback(conn, 1, [])

        conn.cursor.assert_not_called()
