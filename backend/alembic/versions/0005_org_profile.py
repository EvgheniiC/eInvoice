"""Organization firm profile for Steuerberater packages.

Revision ID: 0005_org_profile
Revises: 0004_invoice_history
Create Date: 2026-08-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_org_profile"
down_revision: Union[str, None] = "0004_invoice_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("tax_number", sa.String(length=32), nullable=True))
    op.add_column("organizations", sa.Column("vat_id", sa.String(length=16), nullable=True))
    op.add_column("organizations", sa.Column("iban", sa.String(length=34), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("accountant_email", sa.String(length=254), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "accountant_email")
    op.drop_column("organizations", "iban")
    op.drop_column("organizations", "vat_id")
    op.drop_column("organizations", "tax_number")
