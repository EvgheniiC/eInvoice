"""Seller contact and default buyer fields for outgoing e-invoices.

Revision ID: 0011_org_invoice_contact
Revises: 0010_stripe_billing
Create Date: 2026-11-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_org_invoice_contact"
down_revision: Union[str, None] = "0010_stripe_billing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("invoice_contact_name", sa.String(length=200), nullable=True))
    op.add_column("organizations", sa.Column("invoice_phone", sa.String(length=40), nullable=True))
    op.add_column("organizations", sa.Column("invoice_email", sa.String(length=254), nullable=True))
    op.add_column("organizations", sa.Column("default_buyer_email", sa.String(length=254), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("default_buyer_reference", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "default_buyer_reference")
    op.drop_column("organizations", "default_buyer_email")
    op.drop_column("organizations", "invoice_email")
    op.drop_column("organizations", "invoice_phone")
    op.drop_column("organizations", "invoice_contact_name")
