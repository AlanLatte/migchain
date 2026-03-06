"""Logging configuration."""

import logging


def setup_logging(verbosity: int = 1) -> None:
    """Configure logging with classic format."""
    levels = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    level = levels.get(verbosity, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("yoyo").setLevel(
        logging.INFO if verbosity >= 2 else logging.WARNING,
    )
