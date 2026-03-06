"""extract_database_name -- PostgreSQL DSN parsing.

- simple DSN -> db name
- DSN with query params -> db name (before ?)
- DSN with hyphen/underscore -> correct
- invalid DSN -> ValueError
"""

import pytest

from migchain.application.config import extract_database_name


class TestExtractDatabaseName:
    """Protects the DSN-to-database-name extraction contract."""

    def test_simple_dsn(self):
        """Protects against failure on standard PostgreSQL DSN format."""
        result = extract_database_name("postgresql://user:pass@localhost:5432/mydb")

        assert result == "mydb"

    def test_with_query_params(self):
        """Protects against query parameters leaking into the database name."""
        result = extract_database_name(
            "postgresql://user:pass@localhost:5432/mydb?sslmode=require",
        )

        assert result == "mydb"

    def test_without_port(self):
        """Protects against failure when port is omitted from the DSN."""
        result = extract_database_name("postgresql://user:pass@localhost/testdb")

        assert result == "testdb"

    def test_with_hyphen(self):
        """Protects against hyphens being rejected in database names."""
        result = extract_database_name("postgresql://user:pass@localhost:5432/my-db")

        assert result == "my-db"

    def test_invalid_raises(self):
        """Protects against silently accepting malformed DSNs."""
        with pytest.raises(ValueError, match="Cannot extract database name"):
            extract_database_name("not-a-dsn")

    def test_no_db_name_raises(self):
        """Protects against accepting DSN with missing database component."""
        with pytest.raises(ValueError, match="Cannot extract database name"):
            extract_database_name("postgresql://localhost:")

    def test_psycopg_dsn(self):
        """Protects against failure on psycopg-style driver prefix."""
        result = extract_database_name(
            "postgresql+psycopg://user:pass@localhost:5432/appdb",
        )

        assert result == "appdb"

    def test_with_underscore(self):
        """Protects against underscores being rejected in database names."""
        result = extract_database_name("postgresql://user:pass@localhost:5432/my_db")

        assert result == "my_db"

    def test_ending_with_db_name(self):
        """Protects against failure when DSN ends directly with the database name."""
        result = extract_database_name("postgresql://localhost/finaldb")

        assert result == "finaldb"
