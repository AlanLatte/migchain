"""Presentation layer test fixtures."""

import argparse

import pytest


@pytest.fixture
def base_namespace():
    """Minimal argparse namespace with all required attributes."""
    return argparse.Namespace(
        dsn="postgresql://user:pass@localhost:5432/testdb",
        migrations_dir="./migrations",
        apply=False,
        rollback=False,
        rollback_one=False,
        rollback_latest=False,
        reload=False,
        optimize=False,
        new=False,
        dry_run=False,
        no_inserters=False,
        yes=False,
        include=None,
        exclude=None,
        domain_level=0,
        show_structure=False,
        show_graph=False,
        graph_out=None,
        json_plan_out=None,
        verbose=1,
        quiet=False,
        testing=False,
        gw_count=None,
        gw_template=None,
    )
