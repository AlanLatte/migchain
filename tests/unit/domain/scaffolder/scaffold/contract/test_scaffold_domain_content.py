"""MigrationScaffolder._scaffold_domain -- содержимое файла схемы.

- Создаёт директорию домена
- Генерирует файл с CREATE SCHEMA и DROP SCHEMA
- Содержит docstring, импорт yoyo, steps
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestScaffoldDomainContent:
    """Защищает контракт: _scaffold_domain создаёт валидный файл миграции схемы."""

    def test_creates_domain_directory(self, migrations_root: Path) -> None:
        """Защищает от пропуска создания директории домена."""
        request = ScaffoldRequest(scaffold_type="domain", domain="payments")

        MigrationScaffolder.scaffold(migrations_root, request)

        assert (migrations_root / "payments").is_dir()

    def test_file_contains_create_and_drop_schema(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от неполного содержимого файла схемы."""
        request = ScaffoldRequest(scaffold_type="domain", domain="payments")

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "CREATE SCHEMA IF NOT EXISTS payments" in content
        assert "DROP SCHEMA IF EXISTS payments CASCADE" in content
        assert "from yoyo import step" in content
        assert "steps = [" in content

    def test_file_contains_domain_docstring(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от отсутствия docstring в сгенерированном файле."""
        request = ScaffoldRequest(scaffold_type="domain", domain="payments")

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "Create payments schema" in content

    def test_file_path_inside_domain_directory(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от создания файла вне директории домена."""
        request = ScaffoldRequest(scaffold_type="domain", domain="payments")

        result = MigrationScaffolder.scaffold(migrations_root, request)

        assert result.file_path.parent == migrations_root / "payments"
