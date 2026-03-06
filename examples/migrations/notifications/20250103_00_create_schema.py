"""Create notifications schema."""

from yoyo import step

steps = [
    step(
        """
            create schema if not exists notifications
        """,
        """
            drop schema if exists notifications cascade
        """,
    ),
]
