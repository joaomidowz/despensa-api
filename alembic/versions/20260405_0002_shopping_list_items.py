"""add shopping list items

Revision ID: 20260405_0002
Revises: 20260404_0001
Create Date: 2026-04-05 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260405_0002"
down_revision = "20260404_0001"
branch_labels = None
depends_on = None


shopping_list_item_source_enum = postgresql.ENUM(
    "MANUAL",
    "INVENTORY",
    "SYSTEM",
    "HISTORY",
    "TEMPLATE",
    name="shopping_list_item_source",
    create_type=False,
)


def _timestamp_default() -> sa.TextClause:
    return sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    shopping_list_item_source_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "shopping_list_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("household_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=True),
        sa.Column("inventory_id", sa.Uuid(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("source", shopping_list_item_source_enum, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("desired_qty", sa.Numeric(12, 3), nullable=False, server_default="1"),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=_timestamp_default()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=_timestamp_default()),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["inventory_id"], ["inventory.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_shopping_list_items_normalized_name",
        "shopping_list_items",
        ["normalized_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_shopping_list_items_normalized_name", table_name="shopping_list_items")
    op.drop_table("shopping_list_items")
    shopping_list_item_source_enum.drop(op.get_bind(), checkfirst=True)
