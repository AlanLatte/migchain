"""Create analytics schema."""

from yoyo import step

steps = [
    step(
        """
            create schema if not exists analytics
        """,
        """
            drop schema if exists analytics cascade
        """,
    ),
]
