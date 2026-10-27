"""Wishlist API Endpoints."""

from fastapi import APIRouter, HTTPException, Query, Path
from backend.app.schemas.wishlist import WishlistItemCreate, WishlistSummaryResponse
from backend.app.services.wishlist_service import wishlist_service

router = APIRouter()

@router.get("/wishlist", response_model=WishlistSummaryResponse, tags=["Wishlist"])
def get_wishlist(user_id: str = Query("guest_user", description="User identifier")):
    """Get all items saved in user's wishlist."""
    return wishlist_service.get_wishlist(user_id=user_id)


@router.post("/wishlist", response_model=WishlistSummaryResponse, tags=["Wishlist"])
def add_to_wishlist(item: WishlistItemCreate):
    """Save an item to user's wishlist."""
    try:
        return wishlist_service.add_to_wishlist(
            product_id=item.product_id,
            user_id=item.user_id or "guest_user"
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/wishlist/{product_id}", response_model=WishlistSummaryResponse, tags=["Wishlist"])
def remove_from_wishlist(
    product_id: str = Path(..., description="Product ID to remove from wishlist"),
    user_id: str = Query("guest_user", description="User identifier")
):
    """Remove an item from user's wishlist."""
    return wishlist_service.remove_from_wishlist(product_id=product_id, user_id=user_id)
