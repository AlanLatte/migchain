"""PlainPresenter.setup -- инициализация логирования.

- Устанавливает verbosity на экземпляре
- Вызывает setup_logging с переданным уровнем
"""
# pylint: disable=protected-access

from unittest.mock import patch

from migchain.presentation.plain import PlainPresenter


class TestSetup:
    """Защищает контракт инициализации presenter через setup()."""

    def test_sets_verbosity_and_calls_setup_logging(self):
        """Защищает от потери вызова setup_logging при инициализации."""
        presenter = PlainPresenter()
        with patch(
            "migchain.presentation.plain.setup_logging",
        ) as mock_setup:
            presenter.setup(2)

        assert presenter._verbosity == 2
        mock_setup.assert_called_once_with(2)
