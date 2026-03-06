"""Create auth schema."""

from yoyo import step

steps = [
    step(
        """
            create schema if not exists auth
        """,
        """
            drop schema if exists auth cascade
        """,
    ),
]
