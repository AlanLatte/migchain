"""Global test fixtures for MigChain."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

import pytest


@dataclass
class FakeMigration:
    """Duck-type compatible with yoyo Migration for unit tests."""

    id: str
    path: str = ""
    depends: Set[str] = field(default_factory=set)


@pytest.fixture
def examples_root():
    return Path(__file__).parent.parent / "examples" / "migrations"


@pytest.fixture
def tmp_migrations_root(tmp_path):
    root = tmp_path / "migrations"
    root.mkdir()
    return root
