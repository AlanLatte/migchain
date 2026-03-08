"""PlainPresenter.error -- вывод ошибки с рамкой.

- Логирует сообщение через LOGGER.error
- Оборачивает сообщение в рамку из символов "="
"""

import logging

from migchain.presentation.plain import PlainPresenter


class TestError:
    """Защищает контракт вывода ошибки с рамкой через error."""

    def test_logs_error_with_borders(self, caplog):
        """Защищает от потери рамки или содержимого в error-сообщении."""
        presenter = PlainPresenter()
        with caplog.at_level(logging.ERROR, logger="migchain"):
            presenter.error("Connection failed")

        assert "=" * 60 in caplog.text
        assert "Connection failed" in caplog.text
