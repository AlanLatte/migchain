"""resolve_operation -- interactive fallback via InquirerPy.

- no flags set -> launches interactive select
- returns the value chosen by user
"""

import argparse
from unittest.mock import MagicMock, patch

from migchain.presentation.cli import resolve_operation


class TestInteractiveFallback:
    """Protects the interactive fallback when no operation flag is provided."""

    @patch("migchain.presentation.cli.inquirer")
    def test_no_flags_triggers_interactive(self, mock_inquirer):
        """Protects against silent default when user specifies no operation."""
        mock_prompt = MagicMock()
        mock_prompt.execute.return_value = "rollback"
        mock_inquirer.select.return_value = mock_prompt

        args = argparse.Namespace(
            apply=False,
            rollback=False,
            rollback_one=False,
            rollback_latest=False,
            reload=False,
            optimize=False,
        )
        result = resolve_operation(args)

        assert result == "rollback"
        mock_inquirer.select.assert_called_once()
