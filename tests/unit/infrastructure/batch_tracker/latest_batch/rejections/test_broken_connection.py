"""PostgresBatchTracker.latest_batch -- broken connection handling.

- exception during query -> returns None
"""

from unittest.mock import MagicMock

from migchain.infrastructure.batch_tracker import PostgresBatchTracker, _DatabaseError


class TestBrokenConnection:
    """Protects against crashes when latest_batch query fails."""

    def test_exception_returns_none(self):
        """Protects against unhandled exception when CTE query fails."""
        conn = MagicMock()
        conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=_DatabaseError("connection lost"),
        )
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = PostgresBatchTracker.latest_batch(conn)

        assert result is None
