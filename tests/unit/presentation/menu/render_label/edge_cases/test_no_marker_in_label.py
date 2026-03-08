"""_render_label -- label без маркера {key}.

- если {key} отсутствует в label, строка возвращается без изменений
"""

from migchain.presentation.menu import MenuItem, _render_label


class TestNoMarkerInLabel:
    """Защищает от ошибки, когда label не содержит маркер {key}."""

    def test_label_without_marker_unchanged(self):
        """Защищает от исключения при отсутствии {key} маркера."""
        item = MenuItem(key="z", label="no marker here", value="nope")

        result = _render_label(item)

        assert result == "no marker here"
