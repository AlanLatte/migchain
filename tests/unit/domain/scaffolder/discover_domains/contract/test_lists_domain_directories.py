"""MigrationScaffolder.discover_domains -- обнаружение доменов.

- Возвращает отсортированный список имён директорий
- Игнорирует файлы и скрытые/служебные директории
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder


class TestListsDomainDirectories:
    """Защищает контракт: discover_domains возвращает только валидные домены."""

    def test_returns_sorted_domain_names(self, migrations_root: Path) -> None:
        """Защищает от нарушения сортировки возвращаемых доменов."""
        (migrations_root / "billing").mkdir()
        (migrations_root / "auth").mkdir()
        (migrations_root / "catalog").mkdir()

        result = MigrationScaffolder.discover_domains(migrations_root)

        assert result == ["auth", "billing", "catalog"]

    def test_ignores_hidden_directories(self, migrations_root: Path) -> None:
        """Защищает от включения скрытых директорий в результат."""
        (migrations_root / "auth").mkdir()
        (migrations_root / ".hidden").mkdir()
        (migrations_root / "_private").mkdir()

        result = MigrationScaffolder.discover_domains(migrations_root)

        assert result == ["auth"]

    def test_ignores_files(self, migrations_root: Path) -> None:
        """Защищает от включения файлов (не директорий) в результат."""
        (migrations_root / "auth").mkdir()
        (migrations_root / "readme.txt").write_text("info", encoding="utf-8")

        result = MigrationScaffolder.discover_domains(migrations_root)

        assert result == ["auth"]
