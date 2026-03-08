"""resolve_operation -- флаг --new возвращает 'new'.

- args.new=True -> "new"
"""

from migchain.presentation.cli import resolve_operation


class TestNewFlag:
    """Защищает контракт маппинга флага --new в режим 'new'."""

    def test_new_flag_returns_new(self, base_namespace):
        """Защищает от потери маршрута --new -> 'new'."""
        base_namespace.new = True
        assert resolve_operation(base_namespace) == "new"
