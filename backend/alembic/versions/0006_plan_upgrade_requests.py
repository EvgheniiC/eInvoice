"""Manual organization plan upgrade requests.

Revision ID: 0006_plan_upgrade_requests
Revises: 0005_org_profile
Create Date: 2026-08-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_plan_upgrade_requests"
down_revision: Union[str, None] = "0005_org_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plan_upgrade_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("requested_plan", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "requested_plan IN ('plus', 'team')",
            name="ck_plan_upgrade_requests_plan",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_plan_upgrade_requests_status",
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
    )
    op.create_index(
        "ix_plan_upgrade_requests_organization_id",
        "plan_upgrade_requests",
        ["organization_id"],
    )
    op.create_index(
        "ix_plan_upgrade_requests_requested_by_user_id",
        "plan_upgrade_requests",
        ["requested_by_user_id"],
    )
    op.create_index(
        "ix_plan_upgrade_requests_requested_plan",
        "plan_upgrade_requests",
        ["requested_plan"],
    )
    op.create_index(
        "ix_plan_upgrade_requests_status",
        "plan_upgrade_requests",
        ["status"],
    )
    op.create_index(
        "uq_plan_upgrade_requests_pending_org_plan",
        "plan_upgrade_requests",
        ["organization_id", "requested_plan"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
        sqlite_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_plan_upgrade_requests_pending_org_plan",
        table_name="plan_upgrade_requests",
    )
    op.drop_index(
        "ix_plan_upgrade_requests_status",
        table_name="plan_upgrade_requests",
    )
    op.drop_index(
        "ix_plan_upgrade_requests_requested_plan",
        table_name="plan_upgrade_requests",
    )
    op.drop_index(
        "ix_plan_upgrade_requests_requested_by_user_id",
        table_name="plan_upgrade_requests",
    )
    op.drop_index(
        "ix_plan_upgrade_requests_organization_id",
        table_name="plan_upgrade_requests",
    )
    op.drop_table("plan_upgrade_requests")
