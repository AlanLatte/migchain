"""MigrationScaffolder.scaffold -- диспетчеризация по типу inserter.

- scaffold_type="inserter" -> вызывает _scaffold_inserter
- Файл создаётся в поддиректории inserters/
- Возвращает ScaffoldResult с корректным file_path
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestDispatchesInserterType:
    """Защищает контракт: scaffold_type='inserter' делегирует в _scaffold_inserter."""

    def test_creates_file_in_inserters_subdir(self, migrations_root: Path) -> None:
        """Защищает от создания inserter-миграции вне inserters/."""
        request = ScaffoldRequest(
            scaffold_type="inserter",
            domain="billing",
            description="seed-plans",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.exists()
        assert "inserters" in result.file_path.parts
