"""Seed default notification templates."""

from yoyo import step

__depends__ = {"20250103_02_create_templates"}

steps = [
    step(
        """
        insert into notifications.templates (slug, subject, body_html)
        values
            ('welcome', 'Welcome to our platform!', '<h1>Welcome!</h1>'),
            ('password_reset', 'Reset your password', '<h1>Password Reset</h1>'),
            ('subscription_expired', 'Your subscription has expired', '<h1>Subscription Expired</h1>')
        on conflict (slug) do nothing
        """,
        """
        delete from notifications.templates
        where slug in ('welcome', 'password_reset', 'subscription_expired')
        """,
    ),
]
