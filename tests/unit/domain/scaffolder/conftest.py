"""Фикстуры для тестов MigrationScaffolder."""
# pylint: disable=redefined-outer-name

from pathlib import Path

import pytest


@pytest.fixture
def migrations_root(tmp_path: Path) -> Path:
    """Корневая директория миграций внутри tmp_path."""
    root = tmp_path / "migrations"
    root.mkdir()
    return root
