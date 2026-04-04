from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryStatus(str, Enum):
    IN_STOCK = "Em Estoque"
    PURCHASED = "Comprado"
    BUY = "Comprar"


class ProductSummaryResponse(BaseModel):
    product_id: UUID
    name: str
    category: str


class InventoryItemResponse(BaseModel):
    inventory_id: UUID
    product: ProductSummaryResponse
    current_qty: Decimal
    min_qty: Decimal
    status: InventoryStatus
    updated_at: datetime


class CreateInventoryItemRequest(BaseModel):
    product_name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    current_qty: Decimal = Field(..., ge=0)
    min_qty: Decimal = Field(..., ge=0)


class CreateInventoryItemResponse(BaseModel):
    inventory_id: UUID
    message: str


class UpdateInventoryItemRequest(BaseModel):
    current_qty: Decimal | None = Field(default=None, ge=0)
    min_qty: Decimal | None = Field(default=None, ge=0)


class InventoryAmountRequest(BaseModel):
    amount: Decimal = Field(default=Decimal("1.0"), gt=0)


class InventoryAmountResponse(BaseModel):
    inventory_id: UUID
    current_qty: Decimal
    status: InventoryStatus
