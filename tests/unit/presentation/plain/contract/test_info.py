"""PlainPresenter.info -- вывод информационного сообщения.

- Логирует сообщение через LOGGER.info
"""

import logging

from migchain.presentation.plain import PlainPresenter


class TestInfo:
    """Защищает контракт вывода информационного сообщения через info."""

    def test_logs_info_message(self, caplog):
        """Защищает от потери вывода info-сообщения."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.info("Processing migrations")

        assert "Processing migrations" in caplog.text
