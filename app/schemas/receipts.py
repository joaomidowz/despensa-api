from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field, model_validator

from app.schemas.common import PaginatedResponse


class ItemType(str, Enum):
    PRODUCT = "PRODUCT"
    DISCOUNT = "DISCOUNT"


class ReceiptScanRequest(BaseModel):
    image_base64: str


class ReceiptScanItemResponse(BaseModel):
    raw_name: str
    display_name: str
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal = Decimal("0.00")
    total_price: Decimal
    item_type: ItemType = ItemType.PRODUCT


class ReceiptScanResponse(BaseModel):
    market_name: str
    receipt_date: datetime
    total_amount: Decimal
    items: list[ReceiptScanItemResponse]


class ConfirmReceiptItemRequest(BaseModel):
    product_name: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("product_name", "display_name", "raw_name"),
        serialization_alias="product_name",
    )
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_price: Decimal
    item_type: ItemType = ItemType.PRODUCT

    @model_validator(mode="after")
    def validate_item_math(self):
        if self.item_type == ItemType.PRODUCT:
            expected = (self.quantity * self.unit_price) - self.discount_amount
            if abs(expected - self.total_price) > Decimal("0.02"):
                raise ValueError(f"Matematica inconsistente para o produto {self.product_name}")
        elif self.item_type == ItemType.DISCOUNT:
            if (
                self.quantity != Decimal("1")
                or self.unit_price != Decimal("0")
                or self.discount_amount != Decimal("0")
                or self.total_price >= Decimal("0")
            ):
                raise ValueError("Item de desconto global invalido")
        return self


class ConfirmReceiptRequest(BaseModel):
    market_name: str = Field(..., min_length=1)
    receipt_date: datetime
    total_amount: Decimal = Field(..., gt=0)
    items: list[ConfirmReceiptItemRequest] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_global_rules(self):
        if not any(item.item_type == ItemType.PRODUCT for item in self.items):
            raise ValueError("O recibo deve conter ao menos um produto")
        calculated_total = sum(item.total_price for item in self.items)
        if abs(calculated_total - self.total_amount) > Decimal("0.02"):
            raise ValueError("Soma dos itens diverge do total da nota")
        return self


class ConfirmReceiptResponse(BaseModel):
    message: str
    receipt_id: UUID
    items_processed: int


class ReceiptListItemResponse(BaseModel):
    receipt_id: UUID
    market_name: str
    receipt_date: datetime
    total_amount: Decimal


class PaginatedReceiptsResponse(PaginatedResponse[ReceiptListItemResponse]):
    pass


class ReceiptDetailItemResponse(BaseModel):
    product_id: UUID | None = None
    name: str
    category: str | None = None
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    total_price: Decimal
    item_type: ItemType = ItemType.PRODUCT


class ReceiptDetailResponse(BaseModel):
    receipt_id: UUID
    market_name: str
    receipt_date: datetime
    total_amount: Decimal
    items: list[ReceiptDetailItemResponse]
