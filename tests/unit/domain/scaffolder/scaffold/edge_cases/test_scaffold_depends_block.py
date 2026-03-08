"""MigrationScaffolder.scaffold -- edge cases с блоком __depends__.

- Если в домене уже есть миграции -> __depends__ содержит последнюю
- Если в домене нет миграций -> __depends__ отсутствует
"""

from pathlib import Path

from migchain.domain.scaffolder import MigrationScaffolder, ScaffoldRequest


class TestScaffoldDependsBlock:
    """Защищает граничные случаи: __depends__ при наличии миграций."""

    def test_depends_present_when_prior_migrations_exist(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от потери зависимости при наличии предыдущих миграций."""
        domain_dir = migrations_root / "auth"
        domain_dir.mkdir(parents=True)
        existing = domain_dir / "20250101_00_AAAAA-auth-create-schema.py"
        existing.write_text("steps = []", encoding="utf-8")

        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
            description="add-users",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "__depends__" in content
        assert "20250101_00_AAAAA-auth-create-schema" in content

    def test_no_depends_when_no_prior_migrations(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от появления пустого __depends__ без предыдущих миграций."""
        request = ScaffoldRequest(
            scaffold_type="table",
            domain="auth",
            description="first-migration",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "__depends__" not in content

    def test_inserter_depends_present_when_prior_migrations_exist(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от потери зависимости для inserter."""
        domain_dir = migrations_root / "billing"
        domain_dir.mkdir(parents=True)
        existing = domain_dir / "20250101_00_BBBBB-billing-create-schema.py"
        existing.write_text("steps = []", encoding="utf-8")

        request = ScaffoldRequest(
            scaffold_type="inserter",
            domain="billing",
            description="seed-plans",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "__depends__" in content
        assert "20250101_00_BBBBB-billing-create-schema" in content

    def test_inserter_no_depends_when_no_prior_migrations(
        self,
        migrations_root: Path,
    ) -> None:
        """Защищает от пустого __depends__ для inserter без миграций."""
        request = ScaffoldRequest(
            scaffold_type="inserter",
            domain="billing",
            description="seed-plans",
        )

        result = MigrationScaffolder.scaffold(migrations_root, request)

        content = result.file_path.read_text(encoding="utf-8")
        assert "__depends__" not in content
