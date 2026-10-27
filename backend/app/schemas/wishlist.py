"""Wishlist Pydantic Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field

class WishlistItemCreate(BaseModel):
    product_id: str = Field(..., description="Target product identifier")
    user_id: Optional[str] = Field("guest_user", description="Identifier of the user")


class WishlistItemResponse(BaseModel):
    product_id: str
    title: str
    category: str
    price_inr: int
    review_count: int
    formatted_price: str


class WishlistSummaryResponse(BaseModel):
    items: List[WishlistItemResponse]
    total_items: int
