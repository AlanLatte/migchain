"""Optimizer integration test fixtures — synthetic migrations with redundancies."""

import pytest


@pytest.fixture
def redundant_migrations(tmp_path):
    """Migration tree with a deliberate redundant dependency.

    Graph: A (schema) -> B (table) -> C (table) -> D (table, depends A,C)
    D -> A is redundant because D -> C -> B -> A already exists.
    """
    root = tmp_path / "migrations"
    domain = root / "test_domain"
    domain.mkdir(parents=True)

    (domain / "0001_create_schema.py").write_text(
        '"""Create test schema."""\n'
        "from yoyo import step\n\n"
        "steps = [\n"
        '    step("CREATE SCHEMA IF NOT EXISTS test_domain",\n'
        '         "DROP SCHEMA IF EXISTS test_domain CASCADE"),\n'
        "]\n",
    )

    (domain / "0002_create_alpha.py").write_text(
        '"""Create alpha table."""\n'
        "from yoyo import step\n\n"
        '__depends__ = {"0001_create_schema"}\n\n'
        "steps = [\n"
        "    step(\n"
        '"CREATE TABLE test_domain.alpha '
        '(id serial PRIMARY KEY, name text NOT NULL)",\n'
        '        "DROP TABLE IF EXISTS test_domain.alpha",\n'
        "    ),\n"
        "]\n",
    )

    (domain / "0003_create_beta.py").write_text(
        '"""Create beta table."""\n'
        "from yoyo import step\n\n"
        '__depends__ = {"0002_create_alpha"}\n\n'
        "steps = [\n"
        "    step(\n"
        '"CREATE TABLE test_domain.beta '
        "(id serial PRIMARY KEY, "
        'alpha_id int REFERENCES test_domain.alpha(id))",\n'
        '        "DROP TABLE IF EXISTS test_domain.beta",\n'
        "    ),\n"
        "]\n",
    )

    (domain / "0004_create_gamma.py").write_text(
        '"""Create gamma table — depends on schema AND beta (schema is redundant)."""\n'
        "from yoyo import step\n\n"
        '__depends__ = {"0001_create_schema", "0003_create_beta"}\n\n'
        "steps = [\n"
        "    step(\n"
        '"CREATE TABLE test_domain.gamma '
        "(id serial PRIMARY KEY, "
        'beta_id int REFERENCES test_domain.beta(id))",\n'
        '        "DROP TABLE IF EXISTS test_domain.gamma",\n'
        "    ),\n"
        "]\n",
    )

    return root


@pytest.fixture
def minimal_migrations(tmp_path):
    """Migration tree with no redundancies — already minimal."""
    root = tmp_path / "migrations"
    domain = root / "test_domain"
    domain.mkdir(parents=True)

    (domain / "0001_create_schema.py").write_text(
        '"""Create test schema."""\n'
        "from yoyo import step\n\n"
        "steps = [\n"
        '    step("CREATE SCHEMA IF NOT EXISTS test_domain",\n'
        '         "DROP SCHEMA IF EXISTS test_domain CASCADE"),\n'
        "]\n",
    )

    (domain / "0002_create_table.py").write_text(
        '"""Create a table."""\n'
        "from yoyo import step\n\n"
        '__depends__ = {"0001_create_schema"}\n\n'
        "steps = [\n"
        "    step(\n"
        '        "CREATE TABLE test_domain.items (id serial PRIMARY KEY, name text)",\n'
        '        "DROP TABLE IF EXISTS test_domain.items",\n'
        "    ),\n"
        "]\n",
    )

    return root
