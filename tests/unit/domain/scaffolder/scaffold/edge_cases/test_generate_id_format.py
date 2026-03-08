"""MigrationScaffolder._generate_id -- формат генерируемого идентификатора.

- Начинается с даты в формате YYYYMMDD
- Содержит двузначный порядковый номер
- Содержит 5-символьный случайный суффикс
- Имя домена и описание включены через дефис
- Порядковый номер увеличивается при наличии существующих файлов
- Subdirectory включается в name_part
"""
# pylint: disable=protected-access

import re
from datetime import date
from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder


class TestGenerateIdFormat:
    """Защищает контракт: формат migration_id соответствует шаблону."""

    def test_starts_with_today_date(self, migrations_root: Path) -> None:
        """Защищает от неверного формата даты в идентификаторе."""
        target_dir = migrations_root / "auth"
        target_dir.mkdir(parents=True)

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "",
            "create-schema",
        )

        today = date.today().strftime("%Y%m%d")
        assert result.startswith(today)

    def test_full_format_matches_pattern(self, migrations_root: Path) -> None:
        """Защищает от нарушения общего формата YYYYMMDD_NN_XXXXX-parts."""
        target_dir = migrations_root / "auth"
        target_dir.mkdir(parents=True)

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "",
            "create-schema",
        )

        pattern = r"^\d{8}_\d{2}_[a-zA-Z]{5}-auth-create-schema$"
        assert re.match(pattern, result), f"{result} does not match {pattern}"

    def test_sequence_number_increments(self, migrations_root: Path) -> None:
        """Защищает от неверного подсчёта порядкового номера."""
        target_dir = migrations_root / "auth"
        target_dir.mkdir(parents=True)

        today = date.today().strftime("%Y%m%d")
        (target_dir / f"{today}_00_AAAAA-auth-create-schema.py").write_text(
            "",
            encoding="utf-8",
        )
        (target_dir / f"{today}_01_BBBBB-auth-add-users.py").write_text(
            "",
            encoding="utf-8",
        )

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "",
            "add-roles",
        )

        assert f"{today}_02_" in result

    def test_includes_subdirectory_in_name(self, migrations_root: Path) -> None:
        """Защищает от потери subdirectory в name_part идентификатора."""
        target_dir = migrations_root / "auth" / "users"
        target_dir.mkdir(parents=True)

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "users",
            "create-table",
        )

        assert "auth-users-create-table" in result

    def test_nested_subdirectory_splits_into_parts(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от неправильного разбиения вложенных поддиректорий."""
        target_dir = migrations_root / "auth" / "users" / "profiles"
        target_dir.mkdir(parents=True)

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "users/profiles",
            "add-avatar",
        )

        assert "auth-users-profiles-add-avatar" in result

    def test_empty_dir_starts_at_zero(self, migrations_root: Path) -> None:
        """Защищает от ненулевого начала нумерации в пустой директории."""
        target_dir = migrations_root / "auth"
        target_dir.mkdir(parents=True)

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "",
            "init",
        )

        today = date.today().strftime("%Y%m%d")
        assert f"{today}_00_" in result

    def test_random_suffix_is_five_letters(self, migrations_root: Path) -> None:
        """Защищает от неверной длины случайного суффикса."""
        target_dir = migrations_root / "auth"
        target_dir.mkdir(parents=True)

        result = MigrationScaffolder._generate_id(
            target_dir,
            "auth",
            "",
            "test",
        )

        suffix = result.split("_")[2].split("-")[0]
        assert len(suffix) == 5
        assert suffix.isalpha()
