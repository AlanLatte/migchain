"""Seed default billing plans."""

from yoyo import step

__depends__ = {"20250102_01_create_plans"}

steps = [
    step(
        """
        insert into billing.plans (name, price_cents, interval)
        values
            ('free', 0, 'monthly'),
            ('starter', 990, 'monthly'),
            ('pro', 2990, 'monthly'),
            ('enterprise', 9990, 'monthly')
        on conflict (name) do nothing
        """,
        """
        delete from billing.plans
        where name in ('free', 'starter', 'pro', 'enterprise')
        """,
    ),
]
