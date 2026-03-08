"""_render_label -- замена маркера {key} на ANSI-подсветку.

- {key} в label заменяется на CYAN + key + RESET
- остальная часть label остается без изменений
"""

from migchain.presentation.menu import _CYAN, _RESET, MenuItem, _render_label


class TestReplacesKeyMarker:
    """Защищает контракт замены {key} маркера на ANSI-подсветку."""

    def test_replaces_key_with_ansi(self):
        """Защищает от потери ANSI-кодов при замене маркера."""
        item = MenuItem(key="a", label="{a}pply pending", value="apply")

        result = _render_label(item)

        assert result == f"{_CYAN}a{_RESET}pply pending"

    def test_uppercase_key(self):
        """Защищает от ошибки при заглавной букве в маркере."""
        item = MenuItem(key="R", label="full {R}eload", value="reload")

        result = _render_label(item)

        assert result == f"full {_CYAN}R{_RESET}eload"

    def test_key_at_end_of_label(self):
        """Защищает от ошибки замены маркера в конце строки."""
        item = MenuItem(key="x", label="inde{x}", value="index")

        result = _render_label(item)

        assert result == f"inde{_CYAN}x{_RESET}"
