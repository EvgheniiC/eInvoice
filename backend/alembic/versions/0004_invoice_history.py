"""Invoice history metadata and org consent flags.

Revision ID: 0004_invoice_history
Revises: 0003_batch_jobs
Create Date: 2026-08-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_invoice_history"
down_revision: Union[str, None] = "0003_batch_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("history_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "store_originals_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("history_enabled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "invoice_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("seller_name", sa.String(length=255), nullable=True),
        sa.Column("invoice_number", sa.String(length=128), nullable=True),
        sa.Column("issue_date", sa.String(length=32), nullable=True),
        sa.Column("gross_amount", sa.String(length=32), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("batch_job_id", sa.Uuid(), nullable=True),
        sa.Column("original_storage_path", sa.String(length=512), nullable=True),
        sa.Column("original_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["batch_job_id"], ["batch_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoice_history_organization_id", "invoice_history", ["organization_id"])
    op.create_index("ix_invoice_history_processed_at", "invoice_history", ["processed_at"])
    op.create_index("ix_invoice_history_file_hash", "invoice_history", ["file_hash"])
    op.create_index("ix_invoice_history_created_by_user_id", "invoice_history", ["created_by_user_id"])
    op.create_index("ix_invoice_history_batch_job_id", "invoice_history", ["batch_job_id"])


def downgrade() -> None:
    op.drop_index("ix_invoice_history_batch_job_id", table_name="invoice_history")
    op.drop_index("ix_invoice_history_created_by_user_id", table_name="invoice_history")
    op.drop_index("ix_invoice_history_file_hash", table_name="invoice_history")
    op.drop_index("ix_invoice_history_processed_at", table_name="invoice_history")
    op.drop_index("ix_invoice_history_organization_id", table_name="invoice_history")
    op.drop_table("invoice_history")
    op.drop_column("organizations", "history_enabled_at")
    op.drop_column("organizations", "store_originals_enabled")
    op.drop_column("organizations", "history_enabled")
