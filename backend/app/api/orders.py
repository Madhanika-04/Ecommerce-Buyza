"""Orders and Simulated Checkout API Endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Path
from backend.app.schemas.order import OrderCreate, OrderResponse
from backend.app.services.order_service import order_service

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
def place_order(order_data: OrderCreate):
    """
    Simulate order checkout.
    Validates delivery address & Indian PIN code, converts cart items into a confirmed order,
    and clears the cart.
    """
    try:
        return order_service.create_simulated_order(order_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def list_orders(user_id: str = Query("guest_user", description="User identifier")):
    """List historical confirmed orders for a user."""
    return order_service.get_user_orders(user_id=user_id)


@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order_by_id(
    order_id: str = Path(..., description="Unique Order ID"),
    user_id: str = Query("guest_user", description="User identifier")
):
    """Retrieve full details of an individual order."""
    order = order_service.get_order_by_id(order_id=order_id, user_id=user_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return order
