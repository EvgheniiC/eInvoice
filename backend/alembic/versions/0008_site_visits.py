"""Daily unique site visits for administrator statistics.

Revision ID: 0008_site_visits
Revises: 0007_billing_checkout
Create Date: 2026-10-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_site_visits"
down_revision: Union[str, None] = "0007_billing_checkout"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "site_visits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("visitor_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("visit_date", "visitor_key", name="uq_site_visit_day"),
    )
    op.create_index("ix_site_visits_visit_date", "site_visits", ["visit_date"])


def downgrade() -> None:
    op.drop_index("ix_site_visits_visit_date", table_name="site_visits")
    op.drop_table("site_visits")
