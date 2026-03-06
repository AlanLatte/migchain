"""PostgresBatchTracker.ensure_ready -- table and index creation.

- creates _yoyo_migration_batches table
- creates idx_batch_number, idx_migration_id, idx_applied_at indexes
"""

import psycopg
import pytest

from migchain.infrastructure.batch_tracker import PostgresBatchTracker


@pytest.mark.integration
class TestCreatesTable:
    """Protects the DDL contract for batch tracking table creation."""

    def test_creates_table(self, clean_batch_table: psycopg.Connection):
        """Protects against table not being created by ensure_ready."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        with clean_batch_table.cursor() as cur:
            cur.execute(
                "SELECT table_name "
                "FROM information_schema.tables "
                "WHERE table_schema = 'public' "
                "AND table_name = '_yoyo_migration_batches'",
            )
            result = cur.fetchone()

        assert result is not None
        assert result[0] == "_yoyo_migration_batches"

    def test_indexes_created(self, clean_batch_table: psycopg.Connection):
        """Protects against missing indexes on the batch tracking table."""
        tracker = PostgresBatchTracker()
        tracker.ensure_ready(clean_batch_table)

        with clean_batch_table.cursor() as cur:
            cur.execute(
                "SELECT indexname "
                "FROM pg_indexes "
                "WHERE tablename = '_yoyo_migration_batches'",
            )
            index_names = [row[0] for row in cur.fetchall()]

        assert "idx_batch_number" in index_names
        assert "idx_migration_id" in index_names
        assert "idx_applied_at" in index_names
