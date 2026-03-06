"""PostgresBatchTracker.ensure_ready -- broken connection handling.

- connection that raises on cursor -> logs warning, does not crash
- rollback failure during error handling -> silently ignored
"""

from unittest.mock import MagicMock

from migchain.infrastructure.batch_tracker import PostgresBatchTracker, _DatabaseError


class TestBrokenConnection:
    """Protects against crashes when the database connection is broken."""

    def test_exception_during_create_table_logs_warning(self):
        """Protects against unhandled exception when CREATE TABLE fails."""
        conn = MagicMock()
        conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=_DatabaseError("connection lost"),
        )
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        tracker = PostgresBatchTracker()
        tracker.ensure_ready(conn)

        conn.rollback.assert_called_once()

    def test_rollback_failure_silently_ignored(self):
        """Protects against double-crash when rollback also fails."""
        conn = MagicMock()
        conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=_DatabaseError("connection lost"),
        )
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        conn.rollback.side_effect = _DatabaseError("rollback failed too")

        tracker = PostgresBatchTracker()
        tracker.ensure_ready(conn)
