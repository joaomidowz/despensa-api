from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ShoppingListItemSource(str, Enum):
    MANUAL = "MANUAL"
    INVENTORY = "INVENTORY"
    SYSTEM = "SYSTEM"
    HISTORY = "HISTORY"
    TEMPLATE = "TEMPLATE"


class ShoppingListItemResponse(BaseModel):
    shopping_list_item_id: UUID
    product_id: UUID | None = None
    inventory_id: UUID | None = None
    source: ShoppingListItemSource
    name: str
    category: str | None = None
    notes: str | None = None
    desired_qty: Decimal
    estimated_unit_price: Decimal | None = None
    checked: bool
    created_at: datetime
    updated_at: datetime


class CreateShoppingListItemRequest(BaseModel):
    name: str = Field(..., min_length=1)
    category: str | None = Field(default=None, min_length=1)
    notes: str | None = None
    desired_qty: Decimal = Field(default=Decimal("1"), gt=0)
    estimated_unit_price: Decimal | None = Field(default=None, ge=0)


class AddInventoryItemToShoppingListRequest(BaseModel):
    inventory_id: UUID
    notes: str | None = None
    desired_qty: Decimal = Field(default=Decimal("1"), gt=0)


class UpdateShoppingListItemRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, min_length=1)
    notes: str | None = None
    desired_qty: Decimal | None = Field(default=None, gt=0)
    estimated_unit_price: Decimal | None = Field(default=None, ge=0)
    checked: bool | None = None


class BulkShoppingListItemCheckedPatch(BaseModel):
    id: UUID
    checked: bool
    ts: int = Field(..., ge=0)


class BulkUpdateShoppingListItemsRequest(BaseModel):
    changes: list[BulkShoppingListItemCheckedPatch] = Field(default_factory=list)


class ShoppingListCatalogItemResponse(BaseModel):
    name: str
    category: str | None = None
    purchase_count: int
    last_purchased_at: datetime
    last_unit_price: Decimal | None = None
