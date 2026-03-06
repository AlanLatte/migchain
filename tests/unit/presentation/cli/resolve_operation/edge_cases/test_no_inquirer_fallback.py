"""resolve_operation -- fallback to 'apply' when InquirerPy unavailable.

- _HAS_INQUIRER=False + no flags -> returns "apply"
"""

import argparse
from unittest.mock import patch

from migchain.presentation.cli import resolve_operation


class TestNoInquirerFallback:
    """Protects against crash when InquirerPy is not installed."""

    @patch("migchain.presentation.cli._HAS_INQUIRER", False)
    def test_returns_apply_without_inquirer(self):
        """Protects against unhandled state when no flags and no InquirerPy."""
        args = argparse.Namespace(
            apply=False,
            rollback=False,
            rollback_one=False,
            rollback_latest=False,
            reload=False,
            optimize=False,
        )
        result = resolve_operation(args)

        assert result == "apply"
