"""MenuItem, MenuGroup -- frozen dataclasses.

- MenuItem хранит key, label, value
- MenuGroup хранит title и tuple of MenuItem
- оба класса заморожены (frozen=True)
"""

import pytest

from migchain.presentation.menu import MenuGroup, MenuItem


class TestMenuItemFrozen:
    """Защищает контракт неизменяемости MenuItem."""

    def test_stores_attributes(self):
        """Защищает от потери атрибутов при создании MenuItem."""
        item = MenuItem(key="a", label="{a}pply", value="apply")

        assert item.key == "a"
        assert item.label == "{a}pply"
        assert item.value == "apply"

    def test_is_frozen(self):
        """Защищает от случайного снятия frozen=True с MenuItem."""
        item = MenuItem(key="a", label="{a}pply", value="apply")

        with pytest.raises(AttributeError):
            item.key = "b"  # type: ignore[misc]


class TestMenuGroupFrozen:
    """Защищает контракт неизменяемости MenuGroup."""

    def test_stores_attributes(self):
        """Защищает от потери атрибутов при создании MenuGroup."""
        items = (MenuItem(key="a", label="{a}pply", value="apply"),)
        group = MenuGroup(title="Migrations", items=items)

        assert group.title == "Migrations"
        assert group.items == items

    def test_is_frozen(self):
        """Защищает от случайного снятия frozen=True с MenuGroup."""
        items = (MenuItem(key="a", label="{a}pply", value="apply"),)
        group = MenuGroup(title="Migrations", items=items)

        with pytest.raises(AttributeError):
            group.title = "Other"  # type: ignore[misc]
