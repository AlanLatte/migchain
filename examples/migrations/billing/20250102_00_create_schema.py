"""Create billing schema."""

from yoyo import step

steps = [
    step(
        """
            create schema if not exists billing
        """,
        """
            drop schema if exists billing cascade
        """,
    ),
]
