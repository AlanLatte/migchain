"""resolve_operation -- fallback to 'apply' without presenter.

- no presenter + no flags -> returns "apply"
- presenter returns None (no TTY) -> returns "apply"
"""

import argparse
from unittest.mock import MagicMock

from migchain.presentation.cli import resolve_operation


class TestFallbackToApply:
    """Protects against crash when no interactive selection is possible."""

    def test_returns_apply_without_presenter(self):
        """Protects against unhandled state when no flags and no presenter."""
        args = argparse.Namespace(
            apply=False,
            rollback=False,
            rollback_one=False,
            rollback_latest=False,
            reload=False,
            optimize=False,
            new=False,
        )
        result = resolve_operation(args)

        assert result == "apply"

    def test_returns_apply_when_presenter_returns_none(self):
        """Protects against crash when presenter has no TTY."""
        presenter = MagicMock()
        presenter.select_operation.return_value = None

        args = argparse.Namespace(
            apply=False,
            rollback=False,
            rollback_one=False,
            rollback_latest=False,
            reload=False,
            optimize=False,
            new=False,
        )
        result = resolve_operation(args, presenter)

        assert result == "apply"
