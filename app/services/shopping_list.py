from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainException
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.receipt import ItemType, Receipt, ReceiptItem
from app.models.shopping_list import ShoppingListItem, ShoppingListItemSource
from app.schemas.auth import UserResponse
from app.schemas.shopping_list import (
    AddInventoryItemToShoppingListRequest,
    CreateShoppingListItemRequest,
    ShoppingListCatalogItemResponse,
    ShoppingListItemResponse,
    UpdateShoppingListItemRequest,
)
from app.services.inventory import normalize_product_name


def _serialize(item: ShoppingListItem) -> ShoppingListItemResponse:
    return ShoppingListItemResponse(
        shopping_list_item_id=item.id,
        product_id=item.product_id,
        inventory_id=item.inventory_id,
        source=ShoppingListItemSource(item.source.value),
        name=item.name,
        category=item.category,
        notes=item.notes,
        desired_qty=item.desired_qty,
        estimated_unit_price=item.estimated_unit_price,
        checked=item.checked,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _get_item(db: Session, household_id: UUID, shopping_list_item_id: UUID) -> ShoppingListItem:
    item = db.scalar(
        select(ShoppingListItem).where(
            ShoppingListItem.id == shopping_list_item_id,
            ShoppingListItem.household_id == household_id,
        )
    )
    if item is None:
        raise DomainException.resource_not_found()
    return item


def _get_inventory(db: Session, household_id: UUID, inventory_id: UUID) -> tuple[InventoryItem, Product]:
    row = db.execute(
        select(InventoryItem, Product)
        .join(Product, Product.id == InventoryItem.product_id)
        .where(
            InventoryItem.id == inventory_id,
            InventoryItem.household_id == household_id,
        )
    ).first()
    if row is None:
        raise DomainException.resource_not_found()
    return row


def _lookup_latest_unit_price(
    db: Session,
    household_id: UUID,
    *,
    product_id: UUID | None = None,
    normalized_name: str | None = None,
) -> Decimal | None:
    stmt = (
        select(ReceiptItem.unit_price)
        .join(Receipt, Receipt.id == ReceiptItem.receipt_id)
        .where(
            Receipt.household_id == household_id,
            Receipt.deleted_at.is_(None),
            ReceiptItem.item_type == ItemType.PRODUCT,
        )
        .order_by(Receipt.receipt_date.desc(), Receipt.created_at.desc(), ReceiptItem.id.desc())
        .limit(1)
    )

    if product_id is not None:
        stmt = stmt.where(ReceiptItem.product_id == product_id)
    elif normalized_name is not None:
        stmt = stmt.join(Product, Product.id == ReceiptItem.product_id).where(
            Product.normalized_name == normalized_name
        )
    else:
        return None

    return db.scalar(stmt)


def _find_existing_active_item(
    db: Session,
    household_id: UUID,
    normalized_name: str,
    product_id: UUID | None = None,
) -> ShoppingListItem | None:
    filters = [
        ShoppingListItem.household_id == household_id,
        ShoppingListItem.checked.is_(False),
        ShoppingListItem.normalized_name == normalized_name,
    ]
    if product_id is not None:
        filters.append(
            (ShoppingListItem.product_id == product_id) | (ShoppingListItem.product_id.is_(None))
        )
    return db.scalar(
        select(ShoppingListItem)
        .where(*filters)
        .order_by(ShoppingListItem.updated_at.desc(), ShoppingListItem.created_at.desc())
    )


def list_shopping_list_items(
    db: Session,
    current_user: UserResponse,
) -> list[ShoppingListItemResponse]:
    rows = db.scalars(
        select(ShoppingListItem)
        .where(ShoppingListItem.household_id == current_user.household_id)
        .order_by(ShoppingListItem.checked.asc(), ShoppingListItem.updated_at.desc())
    ).all()
    return [_serialize(item) for item in rows]


def create_shopping_list_item(
    db: Session,
    current_user: UserResponse,
    payload: CreateShoppingListItemRequest,
) -> ShoppingListItemResponse:
    normalized_name = normalize_product_name(payload.name)
    existing_item = _find_existing_active_item(db, current_user.household_id, normalized_name)
    if existing_item is not None:
        raise DomainException.conflict(
            detail="Ja existe um item ativo com este nome na lista de compras.",
            code="SHOPPING_LIST_ITEM_ALREADY_EXISTS",
        )

    now = datetime.now(UTC)
    item = ShoppingListItem(
        household_id=current_user.household_id,
        created_by=current_user.user_id,
        source=ShoppingListItemSource.MANUAL,
        name=payload.name.strip(),
        normalized_name=normalized_name,
        category=_clean_optional_text(payload.category),
        notes=_clean_optional_text(payload.notes),
        desired_qty=payload.desired_qty,
        estimated_unit_price=payload.estimated_unit_price,
        checked=False,
        created_at=now,
        updated_at=now,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


def add_inventory_item_to_shopping_list(
    db: Session,
    current_user: UserResponse,
    payload: AddInventoryItemToShoppingListRequest,
) -> ShoppingListItemResponse:
    inventory_item, product = _get_inventory(db, current_user.household_id, payload.inventory_id)
    normalized_name = normalize_product_name(product.name)
    latest_unit_price = _lookup_latest_unit_price(
        db,
        current_user.household_id,
        product_id=product.id,
        normalized_name=normalized_name,
    )
    existing_item = _find_existing_active_item(
        db,
        current_user.household_id,
        normalized_name,
        product_id=product.id,
    )
    now = datetime.now(UTC)

    if existing_item is not None:
        existing_item.inventory_id = inventory_item.id
        existing_item.product_id = product.id
        existing_item.source = ShoppingListItemSource.INVENTORY
        existing_item.category = product.category
        existing_item.desired_qty += payload.desired_qty
        if existing_item.estimated_unit_price is None:
            existing_item.estimated_unit_price = latest_unit_price
        if existing_item.notes is None:
            existing_item.notes = _clean_optional_text(payload.notes)
        existing_item.updated_at = now
        db.add(existing_item)
        db.commit()
        db.refresh(existing_item)
        return _serialize(existing_item)

    item = ShoppingListItem(
        household_id=current_user.household_id,
        product_id=product.id,
        inventory_id=inventory_item.id,
        created_by=current_user.user_id,
        source=ShoppingListItemSource.INVENTORY,
        name=product.name,
        normalized_name=normalized_name,
        category=product.category,
        notes=_clean_optional_text(payload.notes),
        desired_qty=payload.desired_qty,
        estimated_unit_price=latest_unit_price,
        checked=False,
        created_at=now,
        updated_at=now,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


def update_shopping_list_item(
    db: Session,
    current_user: UserResponse,
    shopping_list_item_id: UUID,
    payload: UpdateShoppingListItemRequest,
) -> ShoppingListItemResponse:
    item = _get_item(db, current_user.household_id, shopping_list_item_id)
    now = datetime.now(UTC)

    if payload.name is not None:
        normalized_name = normalize_product_name(payload.name)
        duplicate = _find_existing_active_item(
            db,
            current_user.household_id,
            normalized_name,
        )
        if duplicate is not None and duplicate.id != item.id:
            raise DomainException.conflict(
                detail="Ja existe um item ativo com este nome na lista de compras.",
                code="SHOPPING_LIST_ITEM_ALREADY_EXISTS",
            )
        item.name = payload.name.strip()
        item.normalized_name = normalized_name

    if "category" in payload.model_fields_set:
        item.category = _clean_optional_text(payload.category)
    if "notes" in payload.model_fields_set:
        item.notes = _clean_optional_text(payload.notes)
    if payload.desired_qty is not None:
        item.desired_qty = payload.desired_qty
    if "estimated_unit_price" in payload.model_fields_set:
        item.estimated_unit_price = payload.estimated_unit_price
    if payload.checked is not None:
        item.checked = payload.checked

    item.updated_at = now
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


def delete_shopping_list_item(
    db: Session,
    current_user: UserResponse,
    shopping_list_item_id: UUID,
) -> None:
    item = _get_item(db, current_user.household_id, shopping_list_item_id)
    db.delete(item)
    db.commit()


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
            last_unit_price=_lookup_latest_unit_price(
                db,
                current_user.household_id,
                normalized_name=normalize_product_name(name),
            ),
        )
        for name, category, purchase_count, last_purchased_at in rows
    ]
