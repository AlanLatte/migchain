"""Create billing plans table."""

from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS billing.plans (
            id SERIAL PRIMARY KEY,
            uuid UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
            name VARCHAR(100) NOT NULL UNIQUE,
            price_cents INTEGER NOT NULL DEFAULT 0,
            interval VARCHAR(20) NOT NULL DEFAULT 'monthly',
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        DROP TABLE IF EXISTS billing.plans
        """,
    ),
]
