"""Stripe customer and subscription ids for paid plans.

Revision ID: 0010_stripe_billing
Revises: 0009_funnel_daily
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_stripe_billing"
down_revision: Union[str, None] = "0009_funnel_daily"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_organizations_stripe_customer_id",
        "organizations",
        ["stripe_customer_id"],
        unique=True,
    )
    op.create_index(
        "ix_organizations_stripe_subscription_id",
        "organizations",
        ["stripe_subscription_id"],
        unique=True,
    )
    op.add_column(
        "billing_checkout_sessions",
        sa.Column("provider_session_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_billing_checkout_sessions_provider_session_id",
        "billing_checkout_sessions",
        ["provider_session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_billing_checkout_sessions_provider_session_id",
        table_name="billing_checkout_sessions",
    )
    op.drop_column("billing_checkout_sessions", "provider_session_id")
    op.drop_index("ix_organizations_stripe_subscription_id", table_name="organizations")
    op.drop_index("ix_organizations_stripe_customer_id", table_name="organizations")
    op.drop_column("organizations", "stripe_subscription_id")
    op.drop_column("organizations", "stripe_customer_id")
