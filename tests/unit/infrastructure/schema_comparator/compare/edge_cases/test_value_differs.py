"""TestcontainerSchemaComparator._compare -- same key, different values.

- same table name with different columns -> "differs" entry
- same index name with different definition -> "differs" entry
- same constraint with different type -> "differs" entry
"""
# pylint: disable=protected-access

from migchain.domain.models import SchemaSnapshot
from migchain.infrastructure.schema_comparator import TestcontainerSchemaComparator


class TestValueDiffers:
    """Protects against _compare missing differences on shared keys."""

    def test_same_table_different_columns(self):
        """Protects against false positive when table exists
        in both but columns differ."""
        original = SchemaSnapshot(
            tables={
                "users": [
                    {"column_name": "id", "data_type": "integer"},
                    {"column_name": "name", "data_type": "text"},
                ],
            },
        )
        optimized = SchemaSnapshot(
            tables={
                "users": [
                    {"column_name": "id", "data_type": "integer"},
                    {"column_name": "email", "data_type": "varchar"},
                ],
            },
        )

        diffs = TestcontainerSchemaComparator._compare(original, optimized)

        assert len(diffs) == 1
        assert "[tables] differs: users" in diffs[0]

    def test_same_index_different_definition(self):
        """Protects against false positive when index name
        matches but definition differs."""
        original = SchemaSnapshot(
            indexes={"idx_users_name": "CREATE INDEX idx_users_name ON users (name)"},
        )
        optimized = SchemaSnapshot(
            indexes={"idx_users_name": "CREATE INDEX idx_users_name ON users (email)"},
        )

        diffs = TestcontainerSchemaComparator._compare(original, optimized)

        assert any("[indexes] differs: idx_users_name" in d for d in diffs)

    def test_same_constraint_different_type(self):
        """Protects against false positive when constraint exists but type differs."""
        original = SchemaSnapshot(
            constraints={"public.users.pk": "PRIMARY KEY(id)"},
        )
        optimized = SchemaSnapshot(
            constraints={"public.users.pk": "UNIQUE(id)"},
        )

        diffs = TestcontainerSchemaComparator._compare(original, optimized)

        assert any("[constraints] differs: public.users.pk" in d for d in diffs)
