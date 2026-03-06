"""Seed default billing plans."""

from yoyo import step

__depends__ = {"20250102_01_create_plans"}

steps = [
    step(
        """
        INSERT INTO billing.plans (name, price_cents, interval)
        VALUES
            ('free', 0, 'monthly'),
            ('starter', 990, 'monthly'),
            ('pro', 2990, 'monthly'),
            ('enterprise', 9990, 'monthly')
        ON CONFLICT (name) DO NOTHING
        """,
        """
        DELETE FROM billing.plans
        WHERE name IN ('free', 'starter', 'pro', 'enterprise')
        """,
    ),
]
