"""Order and Simulated Checkout Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re

class DeliveryAddress(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Customer recipient name")
    phone: str = Field(..., description="Indian 10-digit mobile number")
    address_line: str = Field(..., min_length=5, max_length=255, description="Street address, house no, locality")
    city: str = Field(..., min_length=2, max_length=100, description="City / District")
    state: str = Field(..., min_length=2, max_length=100, description="Indian State")
    pin_code: str = Field(..., description="6-digit Indian Postal PIN Code")
    
    @field_validator("pin_code")
    def validate_indian_pin_code(cls, v: str) -> str:
        clean = v.strip()
        if not re.match(r"^[1-9][0-9]{5}$", clean):
            raise ValueError("Invalid Indian PIN code. Must be a 6-digit number not starting with 0.")
        return clean
        
    @field_validator("phone")
    def validate_indian_phone(cls, v: str) -> str:
        clean = re.sub(r"[^\d]", "", v.strip())
        if len(clean) == 12 and clean.startswith("91"):
            clean = clean[2:]
        if len(clean) != 10:
            raise ValueError("Phone number must be a valid 10-digit Indian mobile number.")
        return clean


class OrderItem(BaseModel):
    product_id: str
    title: str
    price_inr: int
    quantity: int
    subtotal_inr: int
    formatted_price: str
    formatted_subtotal: str


class OrderCreate(BaseModel):
    user_id: Optional[str] = Field("guest_user", description="User or session identifier")
    delivery_address: DeliveryAddress
    payment_method: str = Field("Cash on Delivery (Simulated)", description="Simulated payment option")


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    items: List[OrderItem]
    total_items: int
    total_inr: int
    formatted_total: str
    delivery_address: DeliveryAddress
    payment_method: str
    status: str
    created_at: str
