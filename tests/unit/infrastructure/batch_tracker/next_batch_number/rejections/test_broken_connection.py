"""PostgresBatchTracker.next_batch_number -- broken connection handling.

- exception during query -> returns fallback value 1
"""

from unittest.mock import MagicMock

from migchain.infrastructure.batch_tracker import PostgresBatchTracker, _DatabaseError


class TestBrokenConnection:
    """Protects against crashes when batch number query fails."""

    def test_exception_returns_fallback(self):
        """Protects against unhandled exception when SELECT fails."""
        conn = MagicMock()
        conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=_DatabaseError("connection lost"),
        )
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        result = PostgresBatchTracker.next_batch_number(conn)

        assert result == 1
