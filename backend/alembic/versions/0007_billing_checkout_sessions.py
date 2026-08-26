"""Stub Checkout sessions for plan upgrades.

Revision ID: 0007_billing_checkout
Revises: 0006_plan_upgrade_requests
Create Date: 2026-08-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_billing_checkout"
down_revision: Union[str, None] = "0006_plan_upgrade_requests"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "billing_checkout_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("requested_plan", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "requested_plan IN ('plus', 'team')",
            name="ck_billing_checkout_plan",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'completed', 'expired')",
            name="ck_billing_checkout_status",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_billing_checkout_sessions_organization_id",
        "billing_checkout_sessions",
        ["organization_id"],
    )
    op.create_index(
        "ix_billing_checkout_sessions_requested_by_user_id",
        "billing_checkout_sessions",
        ["requested_by_user_id"],
    )
    op.create_index(
        "ix_billing_checkout_sessions_requested_plan",
        "billing_checkout_sessions",
        ["requested_plan"],
    )
    op.create_index(
        "ix_billing_checkout_sessions_status",
        "billing_checkout_sessions",
        ["status"],
    )
    op.create_index(
        "ix_billing_checkout_sessions_expires_at",
        "billing_checkout_sessions",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_billing_checkout_sessions_expires_at", table_name="billing_checkout_sessions")
    op.drop_index("ix_billing_checkout_sessions_status", table_name="billing_checkout_sessions")
    op.drop_index(
        "ix_billing_checkout_sessions_requested_plan",
        table_name="billing_checkout_sessions",
    )
    op.drop_index(
        "ix_billing_checkout_sessions_requested_by_user_id",
        table_name="billing_checkout_sessions",
    )
    op.drop_index(
        "ix_billing_checkout_sessions_organization_id",
        table_name="billing_checkout_sessions",
    )
    op.drop_table("billing_checkout_sessions")
