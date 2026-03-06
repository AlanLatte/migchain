"""Create subscriptions table with cross-domain dependency on auth.users."""

from yoyo import step

__depends__ = {
    "20250102_01_create_plans",
    "20250101_01_create_users",
}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS billing.subscriptions (
            id SERIAL PRIMARY KEY,
            uuid UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
            user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            plan_id INTEGER NOT NULL REFERENCES billing.plans(id) ON DELETE RESTRICT,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            cancelled_at TIMESTAMP
        )
        """,
        """
        DROP TABLE IF EXISTS billing.subscriptions
        """,
    ),
    step(
        """
        CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id
            ON billing.subscriptions(user_id)
        """,
        """
        DROP INDEX IF EXISTS billing.idx_subscriptions_user_id
        """,
    ),
]
