"""MigrationScaffolder.discover_domains -- пустой и несуществующий корень.

- Пустая директория -> пустой список
- Несуществующая директория -> пустой список
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder


class TestEmptyAndNonexistent:
    """Защищает граничные случаи: пустой и несуществующий корень миграций."""

    def test_empty_root_returns_empty_list(self, migrations_root: Path) -> None:
        """Защищает от ошибки при пустой корневой директории."""
        result = MigrationScaffolder.discover_domains(migrations_root)

        assert result == []

    def test_nonexistent_root_returns_empty_list(self, tmp_path: Path) -> None:
        """Защищает от FileNotFoundError при несуществующей директории."""
        nonexistent = tmp_path / "nonexistent"

        result = MigrationScaffolder.discover_domains(nonexistent)

        assert result == []
