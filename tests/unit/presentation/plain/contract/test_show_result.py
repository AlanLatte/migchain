"""PlainPresenter.show_result -- вывод результата.

- Логирует сообщение через LOGGER.info
"""

import logging

from migchain.presentation.plain import PlainPresenter


class TestShowResult:
    """Защищает контракт вывода результата через show_result."""

    def test_logs_message(self, caplog):
        """Защищает от потери вывода сообщения результата."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.INFO, logger="migchain"):
            presenter.show_result("Migration applied successfully")

        assert "Migration applied successfully" in caplog.text
