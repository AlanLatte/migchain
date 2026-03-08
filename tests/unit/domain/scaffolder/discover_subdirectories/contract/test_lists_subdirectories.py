"""MigrationScaffolder.discover_subdirectories -- обнаружение поддиректорий.

- Возвращает отсортированный список поддиректорий домена
- Игнорирует скрытые и служебные директории
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder


class TestListsSubdirectories:
    """Защищает контракт: discover_subdirectories возвращает валидные поддиректории."""

    def test_returns_sorted_subdirectory_names(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от нарушения сортировки поддиректорий."""
        domain_dir = migrations_root / "auth"
        (domain_dir / "users").mkdir(parents=True)
        (domain_dir / "roles").mkdir()
        (domain_dir / "permissions").mkdir()

        result = MigrationScaffolder.discover_subdirectories(
            migrations_root,
            "auth",
        )

        assert result == ["permissions", "roles", "users"]

    def test_ignores_hidden_and_private_subdirectories(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от включения скрытых/служебных поддиректорий."""
        domain_dir = migrations_root / "auth"
        (domain_dir / "users").mkdir(parents=True)
        (domain_dir / ".cache").mkdir()
        (domain_dir / "_internal").mkdir()

        result = MigrationScaffolder.discover_subdirectories(
            migrations_root,
            "auth",
        )

        assert result == ["users"]
