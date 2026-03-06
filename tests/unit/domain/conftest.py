"""Domain layer test fixtures."""
# pylint: disable=redefined-outer-name

import pytest

from tests.conftest import FakeMigration


@pytest.fixture
def migrations_root(tmp_path):
    """Realistic migration directory tree."""
    dirs = [
        "auth/users",
        "auth/roles",
        "billing/plans/inserters",
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def schema_migration(migrations_root):
    return FakeMigration(
        id="20250101_01_create_users",
        path=str(migrations_root / "auth" / "users" / "20250101_01_create_users.py"),
    )


@pytest.fixture
def inserter_migration(migrations_root):
    return FakeMigration(
        id="20250102_03_seed_plans",
        path=str(
            migrations_root
            / "billing"
            / "plans"
            / "inserters"
            / "20250102_03_seed_plans.py",
        ),
    )


@pytest.fixture
def root_migration(migrations_root):
    return FakeMigration(
        id="20250101_00_create_schema",
        path=str(migrations_root / "auth" / "20250101_00_create_schema.py"),
    )


@pytest.fixture
def linear_chain(migrations_root):
    """A -> B -> C linear dependency chain."""
    a = FakeMigration(
        id="A",
        path=str(migrations_root / "auth" / "users" / "A.py"),
    )
    b = FakeMigration(
        id="B",
        path=str(migrations_root / "auth" / "users" / "B.py"),
        depends={"A"},
    )
    c = FakeMigration(
        id="C",
        path=str(migrations_root / "auth" / "users" / "C.py"),
        depends={"B"},
    )
    return [a, b, c]


@pytest.fixture
def diamond_chain(migrations_root):
    """Diamond: A -> B, A -> C, B -> D, C -> D."""
    a = FakeMigration(
        id="A",
        path=str(migrations_root / "auth" / "users" / "A.py"),
    )
    b = FakeMigration(
        id="B",
        path=str(migrations_root / "auth" / "users" / "B.py"),
        depends={"A"},
    )
    c = FakeMigration(
        id="C",
        path=str(migrations_root / "auth" / "roles" / "C.py"),
        depends={"A"},
    )
    d = FakeMigration(
        id="D",
        path=str(migrations_root / "auth" / "roles" / "D.py"),
        depends={"B", "C"},
    )
    return [a, b, c, d]
