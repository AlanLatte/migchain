"""Create users table."""

from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS auth.users (
            id SERIAL PRIMARY KEY,
            uuid UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        DROP TABLE IF EXISTS auth.users
        """,
    ),
    step(
        """
        CREATE INDEX IF NOT EXISTS idx_users_email
            ON auth.users(email)
        """,
        """
        DROP INDEX IF EXISTS auth.idx_users_email
        """,
    ),
]
