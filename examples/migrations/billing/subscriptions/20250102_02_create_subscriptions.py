"""Create subscriptions table with cross-domain dependency on auth.users."""

from yoyo import step

__depends__ = {
    "20250102_01_create_plans",
    "20250101_01_create_users",
}

steps = [
    step(
        """
        create table if not exists billing.subscriptions (
            id serial primary key,
            uuid uuid not null default gen_random_uuid() unique,
            user_id integer not null references auth.users(id) on delete cascade,
            plan_id integer not null references billing.plans(id) on delete restrict,
            status varchar(20) not null default 'active',
            started_at timestamp not null default current_timestamp,
            expires_at timestamp,
            cancelled_at timestamp
        )
        """,
        """
        drop table if exists billing.subscriptions
        """,
    ),
    step(
        """
        create index if not exists idx_subscriptions_user_id
            on billing.subscriptions(user_id)
        """,
        """
        drop index if exists billing.idx_subscriptions_user_id
        """,
    ),
]
