"""Plan max_parallel and daily usage counters.

Revision ID: 0002_plan_quotas
Revises: 0001_accounts
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_plan_quotas"
down_revision: Union[str, None] = "0001_accounts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "plans",
        sa.Column("max_parallel", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_table(
        "usage_counters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject_type", sa.String(length=16), nullable=False),
        sa.Column("subject_key", sa.String(length=64), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subject_type",
            "subject_key",
            "usage_date",
            "action",
            name="uq_usage_counter_day",
        ),
    )
    op.create_index("ix_usage_counters_subject_type", "usage_counters", ["subject_type"])
    op.create_index("ix_usage_counters_subject_key", "usage_counters", ["subject_key"])
    op.create_index("ix_usage_counters_usage_date", "usage_counters", ["usage_date"])


def downgrade() -> None:
    op.drop_index("ix_usage_counters_usage_date", table_name="usage_counters")
    op.drop_index("ix_usage_counters_subject_key", table_name="usage_counters")
    op.drop_index("ix_usage_counters_subject_type", table_name="usage_counters")
    op.drop_table("usage_counters")
    op.drop_column("plans", "max_parallel")
