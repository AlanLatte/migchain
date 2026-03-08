"""PlainPresenter.debug -- вывод отладочного сообщения.

- Логирует сообщение через LOGGER.debug
"""

import logging

from migchain.presentation.plain import PlainPresenter


class TestDebug:
    """Защищает контракт вывода отладочного сообщения через debug."""

    def test_logs_debug_message(self, caplog):
        """Защищает от потери вывода debug-сообщения."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.DEBUG, logger="migchain"):
            presenter.debug("Resolving dependencies")

        assert "Resolving dependencies" in caplog.text
