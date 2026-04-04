from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.receipt import Receipt
from app.schemas.auth import UserResponse
from app.schemas.overview import OverviewResponse


def _month_window(reference: datetime) -> tuple[datetime, datetime]:
    month_start = datetime(reference.year, reference.month, 1, tzinfo=UTC)
    if reference.month == 12:
        next_month = datetime(reference.year + 1, 1, 1, tzinfo=UTC)
    else:
        next_month = datetime(reference.year, reference.month + 1, 1, tzinfo=UTC)
    return month_start, next_month


def get_overview(db: Session, current_user: UserResponse) -> OverviewResponse:
    household_id = current_user.household_id
    if household_id is None:
        raise ValueError("household_id is required for overview")

    month_start, next_month = _month_window(datetime.now(UTC))

    total_inventory_items = db.scalar(
        select(func.count())
        .select_from(InventoryItem)
        .where(
            InventoryItem.household_id == household_id,
            InventoryItem.current_qty > 0,
        )
    ) or 0

    total_inventory_units = db.scalar(
        select(func.coalesce(func.sum(InventoryItem.current_qty), 0))
        .where(
            InventoryItem.household_id == household_id,
            InventoryItem.current_qty > 0,
        )
    ) or Decimal("0")

    suggested_restock_count = db.scalar(
        select(func.count())
        .select_from(InventoryItem)
        .where(
            InventoryItem.household_id == household_id,
            InventoryItem.current_qty <= InventoryItem.min_qty,
        )
    ) or 0

    low_stock_count = db.scalar(
        select(func.count())
        .select_from(InventoryItem)
        .where(
            InventoryItem.household_id == household_id,
            InventoryItem.current_qty < InventoryItem.min_qty,
        )
    ) or 0

    month_receipts_count = db.scalar(
        select(func.count())
        .select_from(Receipt)
        .where(
            Receipt.household_id == household_id,
            Receipt.deleted_at.is_(None),
            Receipt.receipt_date >= month_start,
            Receipt.receipt_date < next_month,
        )
    ) or 0

    month_receipts_total = db.scalar(
        select(func.coalesce(func.sum(Receipt.total_amount), 0))
        .where(
            Receipt.household_id == household_id,
            Receipt.deleted_at.is_(None),
            Receipt.receipt_date >= month_start,
            Receipt.receipt_date < next_month,
        )
    ) or Decimal("0")

    return OverviewResponse(
        total_inventory_items=int(total_inventory_items),
        total_inventory_units=Decimal(str(total_inventory_units)),
        month_receipts_count=int(month_receipts_count),
        month_receipts_total=Decimal(str(month_receipts_total)),
        suggested_restock_count=int(suggested_restock_count),
        low_stock_count=int(low_stock_count),
    )
