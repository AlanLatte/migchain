"""PlainPresenter.warning -- вывод предупреждения.

- Логирует сообщение через LOGGER.warning
"""

import logging

from migchain.presentation.plain import PlainPresenter


class TestWarning:
    """Защищает контракт вывода предупреждения через warning."""

    def test_logs_warning_message(self, caplog):
        """Защищает от потери вывода предупреждающего сообщения."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.WARNING, logger="migchain"):
            presenter.warning("Deprecated migration format")

        assert "Deprecated migration format" in caplog.text
