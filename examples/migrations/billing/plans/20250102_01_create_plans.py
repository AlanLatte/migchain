"""Create billing plans table."""

from yoyo import step

__depends__ = {"20250102_00_create_schema"}

steps = [
    step(
        """
        create table if not exists billing.plans (
            id serial primary key,
            uuid uuid not null default gen_random_uuid() unique,
            name varchar(100) not null unique,
            price_cents integer not null default 0,
            interval varchar(20) not null default 'monthly',
            is_active boolean not null default true,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        drop table if exists billing.plans
        """,
    ),
]
