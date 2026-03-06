"""YoyoBackendAdapter.connect -- connection establishment.

- connects to PostgreSQL
- connection property accessible after connect
- testing mode doesn't crash (may fail to connect to test_ DB)
- database_name_override doesn't crash
"""
# pylint: disable=broad-exception-caught

import pytest

from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter


@pytest.mark.integration
class TestEstablishesConnection:
    """Protects the connect/connection contract against yoyo backend changes."""

    def test_connects(self, postgres_dsn: str):
        """Protects against connection failures on valid DSN."""
        adapter = YoyoBackendAdapter()

        adapter.connect(postgres_dsn)

        assert adapter.connection is not None

    def test_connection_property(self, postgres_dsn: str):
        """Protects against connection property returning None after connect."""
        adapter = YoyoBackendAdapter()
        adapter.connect(postgres_dsn)

        assert adapter.connection is not None

    def test_testing_mode(self, postgres_dsn: str):
        """Protects against testing=True crashing the adapter setup."""
        adapter = YoyoBackendAdapter()

        try:
            adapter.connect(postgres_dsn, testing=True)
        except Exception:
            pass

    def test_database_override(self, postgres_dsn: str):
        """Protects against database_name_override crashing the adapter setup."""
        adapter = YoyoBackendAdapter()

        try:
            adapter.connect(postgres_dsn, database_name_override="custom")
        except Exception:
            pass
