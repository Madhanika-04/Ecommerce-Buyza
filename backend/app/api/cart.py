"""Shopping Cart API Endpoints."""

from fastapi import APIRouter, HTTPException, Query, Path
from backend.app.schemas.cart import CartItemCreate, CartItemUpdate, CartSummaryResponse
from backend.app.services.cart_service import cart_service

router = APIRouter()

@router.get("/cart", response_model=CartSummaryResponse, tags=["Cart"])
def get_cart(user_id: str = Query("guest_user", description="User identifier")):
    """Get all items, quantities, and calculated total for user's cart."""
    return cart_service.get_cart(user_id=user_id)


@router.post("/cart", response_model=CartSummaryResponse, tags=["Cart"])
def add_to_cart(item: CartItemCreate):
    """Add a product to cart or increment quantity."""
    try:
        return cart_service.add_to_cart(
            product_id=item.product_id,
            quantity=item.quantity,
            user_id=item.user_id or "guest_user"
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/cart/{product_id}", response_model=CartSummaryResponse, tags=["Cart"])
def update_cart_quantity(
    product_id: str = Path(..., description="Product ID to update"),
    update_data: CartItemUpdate = ...
):
    """Update quantity of an item in the cart."""
    try:
        return cart_service.update_quantity(
            product_id=product_id,
            quantity=update_data.quantity,
            user_id=update_data.user_id or "guest_user"
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/cart/{product_id}", response_model=CartSummaryResponse, tags=["Cart"])
def remove_from_cart(
    product_id: str = Path(..., description="Product ID to remove"),
    user_id: str = Query("guest_user", description="User identifier")
):
    """Remove a specific item from user's cart."""
    return cart_service.remove_from_cart(product_id=product_id, user_id=user_id)


@router.delete("/cart", response_model=CartSummaryResponse, tags=["Cart"])
def clear_cart(user_id: str = Query("guest_user", description="User identifier")):
    """Clear all items from user's cart."""
    cart_service.clear_cart(user_id=user_id)
    return cart_service.get_cart(user_id=user_id)
