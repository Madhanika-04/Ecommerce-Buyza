"""Cart Pydantic Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field

class CartItemCreate(BaseModel):
    product_id: str = Field(..., description="Target product identifier")
    quantity: int = Field(1, ge=1, le=50, description="Quantity to purchase (1-50)")
    user_id: Optional[str] = Field("guest_user", description="Identifier of the user or session")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, le=50, description="New quantity (1-50)")
    user_id: Optional[str] = Field("guest_user", description="Identifier of the user")


class CartItemResponse(BaseModel):
    product_id: str
    title: str
    category: str
    price_inr: int
    quantity: int
    subtotal_inr: int
    formatted_price: str
    formatted_subtotal: str


class CartSummaryResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_inr: int
    formatted_total: str
