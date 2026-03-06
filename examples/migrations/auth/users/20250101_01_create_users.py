"""Create users table."""

from yoyo import step

__depends__ = {"20250101_00_create_schema"}

steps = [
    step(
        """
        create table if not exists auth.users (
            id serial primary key,
            uuid uuid not null default gen_random_uuid() unique,
            email varchar(255) not null unique,
            password_hash varchar(255) not null,
            is_active boolean not null default true,
            created_at timestamp not null default current_timestamp,
            updated_at timestamp not null default current_timestamp
        )
        """,
        """
        drop table if exists auth.users
        """,
    ),
    step(
        """
        create index if not exists idx_users_email
            on auth.users(email)
        """,
        """
        drop index if exists auth.idx_users_email
        """,
    ),
]
