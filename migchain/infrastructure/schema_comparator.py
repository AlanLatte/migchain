"""Adapter: schema comparison via testcontainers PostgreSQL."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Sequence

import psycopg
from testcontainers.postgres import PostgresContainer
from yoyo import get_backend, read_migrations

from migchain.constants import LOGGER_NAME
from migchain.domain.models import (
    OptimizationVerification,
    SchemaSnapshot,
)

LOGGER = logging.getLogger(LOGGER_NAME)

COLUMNS_QUERY = """
    SELECT
        t.table_name,
        c.column_name,
        c.data_type,
        c.character_maximum_length,
        c.numeric_precision,
        c.numeric_scale,
        c.is_nullable,
        c.column_default
    FROM information_schema.tables t
    JOIN information_schema.columns c
        ON t.table_name = c.table_name
        AND t.table_schema = c.table_schema
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
        AND t.table_type = 'BASE TABLE'
        AND t.table_name NOT LIKE '_yoyo%%'
        AND t.table_name NOT LIKE 'yoyo%%'
    ORDER BY t.table_schema, t.table_name, c.ordinal_position
"""

INDEXES_QUERY = """
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        AND tablename NOT LIKE '_yoyo%%'
        AND tablename NOT LIKE 'yoyo%%'
    ORDER BY indexname
"""

CONSTRAINTS_QUERY = """
    SELECT
        tc.table_schema || '.' || tc.table_name || '.' || tc.constraint_name AS fqn,
        tc.constraint_type,
        string_agg(
            kcu.column_name, ',' ORDER BY kcu.ordinal_position
        ) AS columns
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.table_schema NOT IN ('pg_catalog', 'information_schema')
        AND tc.table_name NOT LIKE '_yoyo%%'
        AND tc.table_name NOT LIKE 'yoyo%%'
    GROUP BY tc.table_schema, tc.table_name, tc.constraint_name, tc.constraint_type
    ORDER BY fqn
"""


class TestcontainerSchemaComparator:
    """Implements SchemaComparator port using testcontainers."""

    def verify(
        self,
        original_paths: Sequence[Path],
        optimized_paths: Sequence[Path],
    ) -> OptimizationVerification:
        """Spin up PG, apply both migration sets, compare schemas."""
        with PostgresContainer("postgres:16-alpine") as container:
            base_url = container.get_connection_url().replace(
                "postgresql+psycopg2://",
                "postgresql://",
            )

            LOGGER.info("[comparator] Applying original migrations")
            original_snap = self._apply_and_snapshot(
                base_url,
                container,
                "migchain_original",
                original_paths,
            )

            LOGGER.info("[comparator] Applying optimized migrations")
            optimized_snap = self._apply_and_snapshot(
                base_url,
                container,
                "migchain_optimized",
                optimized_paths,
            )

        diffs = self._compare(original_snap, optimized_snap)

        return OptimizationVerification(
            is_safe=len(diffs) == 0,
            differences=diffs,
            original_snapshot=original_snap,
            optimized_snapshot=optimized_snap,
        )

    def _apply_and_snapshot(
        self,
        base_url: str,
        _container: PostgresContainer,
        db_name: str,
        migration_paths: Sequence[Path],
    ) -> SchemaSnapshot:
        """Create a database, apply migrations, return schema snapshot."""
        admin_dsn = base_url
        with psycopg.connect(admin_dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
                cur.execute(f"CREATE DATABASE {db_name}")

        db_dsn = self._replace_db_name(base_url, db_name)
        yoyo_dsn = db_dsn.replace("postgresql://", "postgresql+psycopg://")

        migrations = read_migrations(*(str(p) for p in migration_paths))
        backend = get_backend(yoyo_dsn)
        try:
            with backend.lock():
                backend.apply_migrations(backend.to_apply(migrations))
        finally:
            backend.connection.close()

        return self._snapshot(db_dsn)

    @staticmethod
    def _snapshot(dsn: str) -> SchemaSnapshot:
        """Take a normalized schema snapshot via information_schema."""
        tables: Dict[str, List[Dict[str, str]]] = {}
        indexes: Dict[str, str] = {}
        constraints: Dict[str, str] = {}

        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(COLUMNS_QUERY)
                for row in cur.fetchall():
                    table_name = row[0]
                    tables.setdefault(table_name, []).append(
                        {
                            "column_name": row[1],
                            "data_type": row[2],
                            "char_max_length": row[3],
                            "numeric_precision": row[4],
                            "numeric_scale": row[5],
                            "is_nullable": row[6],
                            "column_default": row[7],
                        },
                    )

                cur.execute(INDEXES_QUERY)
                for row in cur.fetchall():
                    indexes[row[0]] = row[1]

                cur.execute(CONSTRAINTS_QUERY)
                for row in cur.fetchall():
                    constraints[row[0]] = f"{row[1]}({row[2]})"

        return SchemaSnapshot(
            tables=tables,
            indexes=indexes,
            constraints=constraints,
        )

    @staticmethod
    def _compare(
        original: SchemaSnapshot,
        optimized: SchemaSnapshot,
    ) -> List[str]:
        """Compare two snapshots, return list of differences."""
        diffs: List[str] = []
        orig = original.as_comparable()
        opt = optimized.as_comparable()

        for section in ("tables", "indexes", "constraints"):
            orig_section = orig.get(section, {})
            opt_section = opt.get(section, {})

            orig_keys = set(orig_section.keys())
            opt_keys = set(opt_section.keys())

            for key in sorted(orig_keys - opt_keys):
                diffs.append(f"[{section}] missing in optimized: {key}")

            for key in sorted(opt_keys - orig_keys):
                diffs.append(f"[{section}] extra in optimized: {key}")

            for key in sorted(orig_keys & opt_keys):
                if orig_section[key] != opt_section[key]:
                    diffs.append(f"[{section}] differs: {key}")

        return diffs

    @staticmethod
    def _replace_db_name(dsn: str, new_db: str) -> str:
        """Replace the database name in a PostgreSQL DSN."""
        return re.sub(r"/(\w+)(\?|$)", f"/{new_db}\\2", dsn)
