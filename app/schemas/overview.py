from decimal import Decimal

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_inventory_items: int
    total_inventory_units: Decimal
    month_receipts_count: int
    month_receipts_total: Decimal
    suggested_restock_count: int
    low_stock_count: int
