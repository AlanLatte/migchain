"""Create analytics user events table with cross-domain dependencies."""

from yoyo import step

__depends__ = {
    "20250104_00_create_schema",
    "20250101_01_create_users",
    "20250102_02_create_subscriptions",
}

steps = [
    step(
        """
        create table if not exists analytics.user_events (
            id bigserial primary key,
            user_id integer not null references auth.users(id) on delete cascade,
            subscription_id integer references billing.subscriptions(id) on delete set null,
            event_type varchar(50) not null,
            properties jsonb not null default '{}',
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        drop table if exists analytics.user_events
        """,
    ),
    step(
        """
        create index if not exists idx_user_events_user_id
            on analytics.user_events(user_id)
        """,
        """
        drop index if exists analytics.idx_user_events_user_id
        """,
    ),
    step(
        """
        create index if not exists idx_user_events_type_created
            on analytics.user_events(event_type, created_at)
        """,
        """
        drop index if exists analytics.idx_user_events_type_created
        """,
    ),
]
