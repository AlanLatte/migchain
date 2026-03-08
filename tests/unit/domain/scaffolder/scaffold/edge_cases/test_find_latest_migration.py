"""MigrationScaffolder._find_latest_migration -- поиск последней миграции.

- Находит последнюю миграцию по сортировке имён
- Игнорирует файлы начинающиеся с _
- Ищет рекурсивно по поддиректориям
- Пустая директория -> None
- Несуществующая директория -> None
"""
# pylint: disable=protected-access

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder


class TestFindLatestMigration:
    """Защищает контракт: возвращает последний по сортировке ID."""

    def test_finds_latest_by_sort_order(self, migrations_root: Path) -> None:
        """Защищает от неверного определения последней миграции."""
        domain_dir = migrations_root / "auth"
        domain_dir.mkdir(parents=True)
        (domain_dir / "20250101_00_AAAAA-auth-first.py").write_text(
            "",
            encoding="utf-8",
        )
        (domain_dir / "20250102_00_BBBBB-auth-second.py").write_text(
            "",
            encoding="utf-8",
        )

        result = MigrationScaffolder._find_latest_migration(domain_dir)

        assert result == "20250102_00_BBBBB-auth-second"

    def test_searches_recursively(self, migrations_root: Path) -> None:
        """Защищает от потери миграций в поддиректориях."""
        domain_dir = migrations_root / "auth"
        domain_dir.mkdir(parents=True)
        subdir = domain_dir / "users"
        subdir.mkdir()
        (domain_dir / "20250101_00_AAAAA-auth-schema.py").write_text(
            "",
            encoding="utf-8",
        )
        (subdir / "20250103_00_CCCCC-auth-users-table.py").write_text(
            "",
            encoding="utf-8",
        )

        result = MigrationScaffolder._find_latest_migration(domain_dir)

        assert result == "20250103_00_CCCCC-auth-users-table"

    def test_ignores_underscore_prefixed_files(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от включения __init__.py и подобных в результат."""
        domain_dir = migrations_root / "auth"
        domain_dir.mkdir(parents=True)
        (domain_dir / "__init__.py").write_text("", encoding="utf-8")
        (domain_dir / "_private.py").write_text("", encoding="utf-8")
        (domain_dir / "20250101_00_AAAAA-auth-schema.py").write_text(
            "",
            encoding="utf-8",
        )

        result = MigrationScaffolder._find_latest_migration(domain_dir)

        assert result == "20250101_00_AAAAA-auth-schema"

    def test_empty_directory_returns_none(self, migrations_root: Path) -> None:
        """Защищает от ошибки при пустой директории без миграций."""
        domain_dir = migrations_root / "auth"
        domain_dir.mkdir(parents=True)

        result = MigrationScaffolder._find_latest_migration(domain_dir)

        assert result is None

    def test_nonexistent_directory_returns_none(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от FileNotFoundError при несуществующей директории."""
        result = MigrationScaffolder._find_latest_migration(
            migrations_root / "nonexistent",
        )

        assert result is None

    def test_directory_with_only_underscore_files_returns_none(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от ложного обнаружения при наличии только служебных файлов."""
        domain_dir = migrations_root / "auth"
        domain_dir.mkdir(parents=True)
        (domain_dir / "__init__.py").write_text("", encoding="utf-8")

        result = MigrationScaffolder._find_latest_migration(domain_dir)

        assert result is None
