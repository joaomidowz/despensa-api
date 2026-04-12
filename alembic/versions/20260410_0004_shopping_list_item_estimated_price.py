"""add estimated price to shopping list items

Revision ID: 20260410_0004
Revises: 20260406_0003
Create Date: 2026-04-10 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260410_0004"
down_revision = "20260406_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "shopping_list_items",
        sa.Column("estimated_unit_price", sa.Numeric(12, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("shopping_list_items", "estimated_unit_price")
