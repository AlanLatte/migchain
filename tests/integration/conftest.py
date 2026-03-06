"""Integration test fixtures — PostgreSQL via testcontainers."""
# pylint: disable=redefined-outer-name,broad-exception-caught

import psycopg
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    """Session-scoped PostgreSQL container."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def postgres_dsn(postgres_container):
    """Normalized DSN from testcontainers."""
    url = postgres_container.get_connection_url()
    return url.replace("postgresql+psycopg2://", "postgresql://")


@pytest.fixture
def pg_connection(postgres_container):
    """Function-scoped raw psycopg connection with rollback cleanup."""
    dsn = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://",
        "postgresql://",
    )
    conn = psycopg.connect(dsn, autocommit=False)
    yield conn
    try:
        conn.rollback()
    except Exception:
        pass
    finally:
        conn.close()


@pytest.fixture
def clean_batch_table(pg_connection):
    """Drops batch tracking table before test."""
    with pg_connection.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS public._yoyo_migration_batches")
    pg_connection.commit()
    return pg_connection
