"""RichPresenter.confirm -- delegates to InquirerPy.

- returns True when user confirms
- returns False when user declines
"""

from unittest.mock import MagicMock, patch

from migchain.presentation.console import RichPresenter


class TestInquirerConfirm:
    """Protects the contract of delegating confirmation to InquirerPy."""

    @patch("migchain.presentation.console.inquirer")
    def test_confirm_returns_true(self, mock_inquirer):
        """Protects against confirm not returning True when user accepts."""
        mock_prompt = MagicMock()
        mock_prompt.execute.return_value = True
        mock_inquirer.confirm.return_value = mock_prompt

        presenter = RichPresenter()
        result = presenter.confirm("Proceed?")

        assert result is True
        mock_inquirer.confirm.assert_called_once_with(
            message="Proceed?",
            default=False,
        )

    @patch("migchain.presentation.console.inquirer")
    def test_confirm_returns_false(self, mock_inquirer):
        """Protects against confirm not returning False when user declines."""
        mock_prompt = MagicMock()
        mock_prompt.execute.return_value = False
        mock_inquirer.confirm.return_value = mock_prompt

        presenter = RichPresenter()
        result = presenter.confirm("Proceed?")

        assert result is False
