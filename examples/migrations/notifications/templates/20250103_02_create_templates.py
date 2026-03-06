"""Create notification templates table."""

from yoyo import step

__depends__ = {"20250103_00_create_schema"}

steps = [
    step(
        """
        create table if not exists notifications.templates (
            id serial primary key,
            uuid uuid not null default gen_random_uuid() unique,
            slug varchar(100) not null unique,
            subject varchar(255) not null,
            body_html text not null,
            body_text text,
            created_at timestamp not null default current_timestamp,
            updated_at timestamp not null default current_timestamp
        )
        """,
        """
        drop table if exists notifications.templates
        """,
    ),
]
