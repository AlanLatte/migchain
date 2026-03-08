"""resolve_operation -- interactive fallback via presenter.

- no flags set -> delegates to presenter.select_operation()
- returns the value chosen by user
"""

import argparse
from unittest.mock import MagicMock

from migchain.presentation.cli import resolve_operation


class TestInteractiveFallback:
    """Protects the interactive fallback when no operation flag is provided."""

    def test_no_flags_delegates_to_presenter(self):
        """Protects against silent default when user specifies no operation."""
        presenter = MagicMock()
        presenter.select_operation.return_value = "rollback"

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

        assert result == "rollback"
        presenter.select_operation.assert_called_once()
