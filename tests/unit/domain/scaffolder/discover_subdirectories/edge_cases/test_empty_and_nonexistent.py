"""MigrationScaffolder.discover_subdirectories -- пустой и несуществующий домен.

- Пустой домен -> пустой список
- Несуществующий домен -> пустой список
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder


class TestEmptyAndNonexistent:
    """Защищает граничные случаи: пустой и несуществующий домен."""

    def test_empty_domain_returns_empty_list(self, migrations_root: Path) -> None:
        """Защищает от ошибки при пустом домене без поддиректорий."""
        (migrations_root / "auth").mkdir()

        result = MigrationScaffolder.discover_subdirectories(
            migrations_root,
            "auth",
        )

        assert result == []

    def test_nonexistent_domain_returns_empty_list(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от FileNotFoundError при несуществующем домене."""
        result = MigrationScaffolder.discover_subdirectories(
            migrations_root,
            "nonexistent",
        )

        assert result == []
