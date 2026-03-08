"""build_config -- операция 'new' создает директорию миграций.

- operation="new" -> migrations_root.mkdir(parents=True, exist_ok=True)
- директория создается если не существует
"""

from migchain.presentation.cli import build_config


class TestNewOperationCreatesDir:
    """Защищает контракт создания директории миграций при операции 'new'."""

    def test_creates_migrations_directory(self, base_namespace, tmp_path):
        """Защищает от ошибки при отсутствии директории миграций для операции 'new'."""
        target = tmp_path / "new_migrations"
        base_namespace.migrations_dir = str(target)
        base_namespace.dsn = ""

        config = build_config(base_namespace, operation="new")

        assert target.resolve().is_dir()
        assert config.migrations_root == target.resolve()
