from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainException
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.receipt import Receipt, ReceiptItem
from app.schemas.auth import UserResponse
from app.schemas.receipts import (
    ConfirmReceiptRequest,
    ConfirmReceiptResponse,
    ItemType,
    PaginatedReceiptsResponse,
    ReceiptDetailItemResponse,
    ReceiptDetailResponse,
    ReceiptListItemResponse,
)
from app.services.inventory import normalize_product_name

_CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Frios", ("mortadela", "presunto", "salame", "peito de peru", "apresuntado", "ham")),
    ("Laticinios", ("queijo", "leite", "iogurte", "manteiga", "requeijao", "creme de leite")),
    ("Carnes", ("carne", "frango", "linguica", "bovina", "suina", "patinho", "acem", "moida")),
    ("Congelados", ("pizza", "lasanha", "nuggets", "hamburguer", "congelad")),
    ("Padaria", ("pao", "bolo", "torrada", "biscoito", "rosquinha")),
    ("Bebidas", ("suco", "refrigerante", "agua", "cerveja", "vinho", "cafe", "cha")),
    ("Hortifruti", ("banana", "maca", "laranja", "alface", "tomate", "cebola", "batata")),
    ("Limpeza", ("detergente", "sabao", "amaciante", "agua sanitaria", "desinfetante", "alvejante")),
    ("Higiene", ("sabonete", "shampoo", "condicionador", "pasta de dente", "papel higienico")),
]


def infer_product_category(product_name: str) -> str:
    normalized_name = normalize_product_name(product_name)
    for category, keywords in _CATEGORY_RULES:
        if any(keyword in normalized_name for keyword in keywords):
            return category
    return "Sem Categoria"


def confirm_receipt(
    db: Session,
    current_user: UserResponse,
    payload: ConfirmReceiptRequest,
) -> ConfirmReceiptResponse:
    receipt = Receipt(
        household_id=current_user.household_id,
        market_name=payload.market_name.strip(),
        total_amount=payload.total_amount,
        receipt_date=payload.receipt_date,
    )

    try:
        db.add(receipt)
        db.flush()

        processed_count = 0
        now = datetime.now(UTC)

        for item in payload.items:
            product_id: UUID | None = None
            category: str | None = None

            if item.item_type == ItemType.PRODUCT:
                normalized_name = normalize_product_name(item.product_name)
                product = db.scalar(select(Product).where(Product.normalized_name == normalized_name))
                if product is None:
                    inferred_category = infer_product_category(item.product_name)
                    product = Product(
                        name=item.product_name.strip(),
                        normalized_name=normalized_name,
                        category=inferred_category,
                    )
                    db.add(product)
                    db.flush()

                product_id = product.id
                category = product.category

                inventory_item = db.scalar(
                    select(InventoryItem).where(
                        InventoryItem.household_id == current_user.household_id,
                        InventoryItem.product_id == product.id,
                    )
                )
                if inventory_item is None:
                    inventory_item = InventoryItem(
                        household_id=current_user.household_id,
                        product_id=product.id,
                        current_qty=item.quantity,
                        min_qty=Decimal("0"),
                        updated_at=now,
                    )
                else:
                    inventory_item.current_qty += item.quantity
                    inventory_item.updated_at = now
                db.add(inventory_item)

            receipt_item = ReceiptItem(
                receipt_id=receipt.id,
                product_id=product_id,
                name=item.product_name.strip(),
                category=category,
                item_type=item.item_type,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_amount=item.discount_amount,
                total_price=item.total_price,
            )
            db.add(receipt_item)
            processed_count += 1

        db.commit()
        db.refresh(receipt)
    except Exception:
        db.rollback()
        raise

    return ConfirmReceiptResponse(
        message="Compra registrada e estoque atualizado com sucesso.",
        receipt_id=receipt.id,
        items_processed=processed_count,
    )


def list_receipts(
    db: Session,
    current_user: UserResponse,
    month: int | None,
    year: int | None,
    limit: int,
    offset: int,
) -> PaginatedReceiptsResponse:
    filters = [
        Receipt.household_id == current_user.household_id,
        Receipt.deleted_at.is_(None),
    ]
    if month is not None:
        filters.append(extract("month", Receipt.receipt_date) == month)
    if year is not None:
        filters.append(extract("year", Receipt.receipt_date) == year)

    total = db.scalar(select(func.count()).select_from(Receipt).where(*filters)) or 0

    rows = db.scalars(
        select(Receipt)
        .where(*filters)
        .order_by(Receipt.receipt_date.desc(), Receipt.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    items = [
        ReceiptListItemResponse(
            receipt_id=row.id,
            market_name=row.market_name,
            receipt_date=row.receipt_date,
            total_amount=row.total_amount,
        )
        for row in rows
    ]

    return PaginatedReceiptsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(items)) < total,
    )


def get_receipt_detail(
    db: Session,
    current_user: UserResponse,
    receipt_id: UUID,
) -> ReceiptDetailResponse:
    receipt = db.scalar(
        select(Receipt).where(
            Receipt.id == receipt_id,
            Receipt.household_id == current_user.household_id,
            Receipt.deleted_at.is_(None),
        )
    )
    if receipt is None:
        raise DomainException.resource_not_found()

    receipt_items = db.scalars(
        select(ReceiptItem).where(ReceiptItem.receipt_id == receipt.id).order_by(ReceiptItem.id.asc())
    ).all()

    return ReceiptDetailResponse(
        receipt_id=receipt.id,
        market_name=receipt.market_name,
        receipt_date=receipt.receipt_date,
        total_amount=receipt.total_amount,
        items=[
            ReceiptDetailItemResponse(
                product_id=item.product_id,
                name=item.name,
                category=item.category,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_amount=item.discount_amount,
                total_price=item.total_price,
                item_type=item.item_type,
            )
            for item in receipt_items
        ],
    )
