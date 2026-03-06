"""Create notification events table with cross-domain dependencies."""

from yoyo import step

__depends__ = {
    "20250101_01_create_users",
    "20250103_02_create_templates",
}

steps = [
    step(
        """
        create table if not exists notifications.events (
            id bigserial primary key,
            uuid uuid not null default gen_random_uuid() unique,
            user_id integer not null references auth.users(id) on delete cascade,
            template_id integer not null references notifications.templates(id) on delete restrict,
            channel varchar(20) not null default 'email',
            status varchar(20) not null default 'pending',
            payload jsonb not null default '{}',
            sent_at timestamp,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        drop table if exists notifications.events
        """,
    ),
    step(
        """
        create index if not exists idx_events_user_id
            on notifications.events(user_id)
        """,
        """
        drop index if exists notifications.idx_events_user_id
        """,
    ),
    step(
        """
        create index if not exists idx_events_status
            on notifications.events(status)
        where status = 'pending'
        """,
        """
        drop index if exists notifications.idx_events_status
        """,
    ),
]
