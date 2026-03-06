"""PostgresBatchTracker._record -- broken connection handling.

- exception during INSERT -> logs warning, does not crash
"""

from unittest.mock import MagicMock

from migchain.infrastructure.batch_tracker import PostgresBatchTracker, _DatabaseError


class TestBrokenConnection:
    """Protects against crashes when recording a batch operation fails."""

    def test_exception_during_insert_logs_warning(self):
        """Protects against unhandled exception when INSERT INTO fails."""
        conn = MagicMock()
        conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=_DatabaseError("connection lost"),
        )
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        tracker = PostgresBatchTracker()
        tracker.record_apply(conn, 1, ["migration_A"])
