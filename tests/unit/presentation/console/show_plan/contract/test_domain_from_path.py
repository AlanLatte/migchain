"""RichPresenter.show_plan -- домен определяется из пути миграции.

- при передаче migrations_root домен извлекается из относительного пути
- домен отображается в выводе плана
"""
# pylint: disable=protected-access

from io import StringIO

from rich.console import Console

from migchain.domain.models import MigrationPlan
from migchain.presentation.console import RichPresenter
from tests.conftest import FakeMigration


def make_presenter():
    presenter = RichPresenter()
    presenter._console = Console(file=StringIO(), force_terminal=True)
    return presenter


def get_output(presenter):
    return presenter._console.file.getvalue()


class TestDomainFromPath:
    """Защищает контракт определения домена из пути к миграции."""

    def test_domain_extracted_from_migrations_root(self, tmp_path):
        """Защищает от потери домена при передаче migrations_root.
        Домен должен извлекаться из относительного пути миграции."""
        migrations_root = tmp_path / "migrations"
        migrations_root.mkdir()
        domain_dir = migrations_root / "users"
        domain_dir.mkdir()

        presenter = make_presenter()
        migration = FakeMigration(
            id="20250101_01_create_users",
            path=str(domain_dir / "20250101_01_create_users.py"),
        )
        plan = MigrationPlan(
            schema_migrations=[migration],
            all_migrations=[migration],
        )

        presenter.show_plan(plan, mode="apply", migrations_root=migrations_root)
        output = get_output(presenter)

        assert "users" in output
