from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.receipt import ItemType, Receipt, ReceiptItem
from app.schemas.auth import UserResponse
from app.schemas.shopping_list import ShoppingListCatalogItemResponse


def list_shopping_list_catalog(
    db: Session,
    current_user: UserResponse,
) -> list[ShoppingListCatalogItemResponse]:
    rows = db.execute(
        select(
            ReceiptItem.name,
            func.max(ReceiptItem.category),
            func.count(ReceiptItem.id),
            func.max(Receipt.receipt_date),
        )
        .join(Receipt, Receipt.id == ReceiptItem.receipt_id)
        .where(
            Receipt.household_id == current_user.household_id,
            Receipt.deleted_at.is_(None),
            ReceiptItem.item_type == ItemType.PRODUCT,
        )
        .group_by(ReceiptItem.name)
        .order_by(func.max(Receipt.receipt_date).desc(), func.count(ReceiptItem.id).desc())
    ).all()

    return [
        ShoppingListCatalogItemResponse(
            name=name,
            category=category,
            purchase_count=purchase_count,
            last_purchased_at=last_purchased_at,
        )
        for name, category, purchase_count, last_purchased_at in rows
    ]
