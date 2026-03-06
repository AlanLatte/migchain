"""Create permissions table."""

from yoyo import step

__depends__ = {"20250101_02_create_roles"}

steps = [
    step(
        """
        create table if not exists auth.permissions (
            id serial primary key,
            uuid uuid not null default gen_random_uuid() unique,
            name varchar(100) not null unique,
            description text,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        drop table if exists auth.permissions
        """,
    ),
    step(
        """
        create table if not exists auth.role_permissions (
            role_id integer not null references auth.roles(id) on delete cascade,
            permission_id integer not null references auth.permissions(id) on delete cascade,
            granted_at timestamp not null default current_timestamp,

            primary key (role_id, permission_id)
        )
        """,
        """
        drop table if exists auth.role_permissions
        """,
    ),
]
