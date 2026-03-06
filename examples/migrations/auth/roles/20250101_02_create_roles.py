"""Create roles and user_roles tables."""

from yoyo import step

__depends__ = {"20250101_01_create_users"}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS auth.roles (
            id SERIAL PRIMARY KEY,
            uuid UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        DROP TABLE IF EXISTS auth.roles
        """,
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS auth.user_roles (
            user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            role_id INTEGER NOT NULL REFERENCES auth.roles(id) ON DELETE CASCADE,
            assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (user_id, role_id)
        )
        """,
        """
        DROP TABLE IF EXISTS auth.user_roles
        """,
    ),
]
