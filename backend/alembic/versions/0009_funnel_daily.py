"""Daily product-action counters for administrator statistics.

Revision ID: 0009_funnel_daily
Revises: 0008_site_visits
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_funnel_daily"
down_revision: Union[str, None] = "0008_site_visits"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "funnel_daily",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("step", sa.String(length=32), nullable=False),
        sa.Column("event_count", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "step IN ('landing', 'upload', 'parse_success', 'export', 'accountant_package')",
            name="ck_funnel_daily_step",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_date", "step", name="uq_funnel_daily_step"),
    )
    op.create_index("ix_funnel_daily_event_date", "funnel_daily", ["event_date"])


def downgrade() -> None:
    op.drop_index("ix_funnel_daily_event_date", table_name="funnel_daily")
    op.drop_table("funnel_daily")
