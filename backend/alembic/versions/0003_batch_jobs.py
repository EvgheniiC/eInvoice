"""Batch job queue for Plus/Team uploads.

Revision ID: 0003_batch_jobs
Revises: 0002_plan_quotas
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_batch_jobs"
down_revision: Union[str, None] = "0002_plan_quotas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "batch_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_batch_jobs_organization_id", "batch_jobs", ["organization_id"])
    op.create_index("ix_batch_jobs_created_by_user_id", "batch_jobs", ["created_by_user_id"])
    op.create_index("ix_batch_jobs_status", "batch_jobs", ["status"])
    op.create_table(
        "batch_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("invoice_number", sa.String(length=128), nullable=True),
        sa.Column("seller_name", sa.String(length=255), nullable=True),
        sa.Column("gross_amount", sa.String(length=32), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["batch_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_batch_items_job_id", "batch_items", ["job_id"])
    op.create_index("ix_batch_items_status", "batch_items", ["status"])


def downgrade() -> None:
    op.drop_index("ix_batch_items_status", table_name="batch_items")
    op.drop_index("ix_batch_items_job_id", table_name="batch_items")
    op.drop_table("batch_items")
    op.drop_index("ix_batch_jobs_status", table_name="batch_jobs")
    op.drop_index("ix_batch_jobs_created_by_user_id", table_name="batch_jobs")
    op.drop_index("ix_batch_jobs_organization_id", table_name="batch_jobs")
    op.drop_table("batch_jobs")
