"""Logging configuration and management."""

import logging


class LoggingManager:
    """Manages logging configuration and operations."""

    LEVELS = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }

    @classmethod
    def setup_logging(cls, verbosity: int = 1) -> None:
        level = cls.LEVELS.get(verbosity, logging.INFO)

        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        yoyo_level = logging.INFO if verbosity >= 2 else logging.WARNING
        logging.getLogger("yoyo").setLevel(yoyo_level)
