from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from unidecode import unidecode

from app.core.exceptions import DomainException
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.schemas.auth import UserResponse
from app.schemas.inventory import (
    CreateInventoryItemRequest,
    CreateInventoryItemResponse,
    InventoryAmountResponse,
    InventoryItemResponse,
    InventoryStatus,
    ProductSummaryResponse,
    UpdateInventoryItemRequest,
)


def normalize_product_name(name: str) -> str:
    parts = unidecode(name).lower().strip().split()
    return " ".join(parts)


def _status_for(current_qty: Decimal, min_qty: Decimal) -> InventoryStatus:
    if current_qty <= min_qty:
        return InventoryStatus.BUY
    return InventoryStatus.IN_STOCK


def _serialize(item: InventoryItem, product: Product) -> InventoryItemResponse:
    return InventoryItemResponse(
        inventory_id=item.id,
        product=ProductSummaryResponse(
            product_id=product.id,
            name=product.name,
            category=product.category,
        ),
        current_qty=item.current_qty,
        min_qty=item.min_qty,
        status=_status_for(item.current_qty, item.min_qty),
        updated_at=item.updated_at,
    )


def _get_inventory_in_household(db: Session, household_id: UUID, inventory_id: UUID) -> InventoryItem:
    item = db.scalar(
        select(InventoryItem).where(
            InventoryItem.id == inventory_id,
            InventoryItem.household_id == household_id,
        )
    )
    if item is None:
        raise DomainException.resource_not_found()
    return item


def _get_product(db: Session, product_id: UUID) -> Product:
    product = db.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise DomainException.resource_not_found()
    return product


def list_inventory(
    db: Session,
    current_user: UserResponse,
    status_filter: str | None,
) -> list[InventoryItemResponse]:
    stmt = select(InventoryItem, Product).join(Product, Product.id == InventoryItem.product_id).where(
        InventoryItem.household_id == current_user.household_id
    )
    rows = db.execute(stmt).all()

    items = [_serialize(inventory_item, product) for inventory_item, product in rows]

    if status_filter is None:
        return items

    normalized = status_filter.strip().lower()
    if normalized == "comprar":
        return [item for item in items if item.status == InventoryStatus.BUY]
    if normalized == "comprado":
        return [item for item in items if item.status == InventoryStatus.PURCHASED]
    if normalized == "estoque":
        return [item for item in items if item.status == InventoryStatus.IN_STOCK]
    raise DomainException(
        detail="Filtro de status invalido. Use 'comprar', 'comprado' ou 'estoque'.",
        code="INVALID_STATUS_FILTER",
        status_code=422,
    )


def create_inventory_item(
    db: Session,
    current_user: UserResponse,
    payload: CreateInventoryItemRequest,
) -> CreateInventoryItemResponse:
    normalized_name = normalize_product_name(payload.product_name)

    product = db.scalar(select(Product).where(Product.normalized_name == normalized_name))
    if product is None:
        product = Product(
            name=payload.product_name.strip(),
            normalized_name=normalized_name,
            category=payload.category.strip(),
        )
        db.add(product)
        db.flush()

    existing_inventory = db.scalar(
        select(InventoryItem).where(
            InventoryItem.household_id == current_user.household_id,
            InventoryItem.product_id == product.id,
        )
    )

    now = datetime.now(UTC)

    if existing_inventory is None:
        inventory = InventoryItem(
            household_id=current_user.household_id,
            product_id=product.id,
            current_qty=payload.current_qty,
            min_qty=payload.min_qty,
            updated_at=now,
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return CreateInventoryItemResponse(
            inventory_id=inventory.id,
            message="Item adicionado ao estoque.",
        )

    existing_inventory.current_qty += payload.current_qty
    existing_inventory.min_qty = payload.min_qty
    existing_inventory.updated_at = now
    db.add(existing_inventory)
    db.commit()
    db.refresh(existing_inventory)
    return CreateInventoryItemResponse(
        inventory_id=existing_inventory.id,
        message="Item adicionado ao estoque.",
    )


def consume_inventory_item(
    db: Session,
    current_user: UserResponse,
    inventory_id: UUID,
    amount: Decimal,
) -> InventoryAmountResponse:
    item = _get_inventory_in_household(db, current_user.household_id, inventory_id)
    if item.current_qty < amount:
        raise DomainException.insufficient_stock()

    item.current_qty -= amount
    item.updated_at = datetime.now(UTC)
    db.add(item)
    db.commit()
    db.refresh(item)

    return InventoryAmountResponse(
        inventory_id=item.id,
        current_qty=item.current_qty,
        status=_status_for(item.current_qty, item.min_qty),
    )


def add_inventory_item(
    db: Session,
    current_user: UserResponse,
    inventory_id: UUID,
    amount: Decimal,
) -> InventoryAmountResponse:
    item = _get_inventory_in_household(db, current_user.household_id, inventory_id)
    item.current_qty += amount
    item.updated_at = datetime.now(UTC)
    db.add(item)
    db.commit()
    db.refresh(item)

    return InventoryAmountResponse(
        inventory_id=item.id,
        current_qty=item.current_qty,
        status=_status_for(item.current_qty, item.min_qty),
    )


def update_inventory_item(
    db: Session,
    current_user: UserResponse,
    inventory_id: UUID,
    payload: UpdateInventoryItemRequest,
) -> InventoryItemResponse:
    item = _get_inventory_in_household(db, current_user.household_id, inventory_id)
    product = _get_product(db, item.product_id)

    if payload.product_name is not None:
        normalized_name = normalize_product_name(payload.product_name)
        existing_product = db.scalar(select(Product).where(Product.normalized_name == normalized_name))
        if existing_product is not None and existing_product.id != product.id:
            raise DomainException.conflict(
                detail="Ja existe outro produto com este nome normalizado.",
                code="PRODUCT_NAME_CONFLICT",
            )
        product.name = payload.product_name.strip()
        product.normalized_name = normalized_name
    if payload.category is not None:
        product.category = payload.category.strip()

    if payload.current_qty is not None:
        item.current_qty = payload.current_qty
    if payload.min_qty is not None:
        item.min_qty = payload.min_qty
    item.updated_at = datetime.now(UTC)
    db.add(item)
    db.add(product)
    db.commit()
    db.refresh(item)
    db.refresh(product)
    return _serialize(item, product)


def delete_inventory_item(db: Session, current_user: UserResponse, inventory_id: UUID) -> None:
    item = _get_inventory_in_household(db, current_user.household_id, inventory_id)
    db.delete(item)
    db.commit()
