"""_short_migration_id -- fallback при отсутствии разделителей.

- Если ID содержит менее 3 частей по "_", возвращается оригинальный ID
"""

from migchain.presentation.plain import _short_migration_id


class TestShortMigrationIdNoUnderscores:
    """Защищает fallback _short_migration_id для нестандартных ID."""

    def test_returns_original_id_without_underscores(self):
        """Защищает от потери оригинального ID при отсутствии разделителей."""
        assert _short_migration_id("simple-migration") == "simple-migration"

    def test_returns_original_id_with_single_underscore(self):
        """Защищает от ошибки при ID с одним разделителем."""
        assert _short_migration_id("20250101_create") == "20250101_create"
