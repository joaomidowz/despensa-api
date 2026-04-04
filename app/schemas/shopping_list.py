from datetime import datetime

from pydantic import BaseModel


class ShoppingListCatalogItemResponse(BaseModel):
    name: str
    category: str | None = None
    purchase_count: int
    last_purchased_at: datetime
