"""
Wishlist Service
================
Manages persistent saved products in MongoDB with fallback.
"""

from typing import Dict, List, Any
from backend.app.db.mongodb import db_manager
from backend.app.services.catalog_service import catalog_service
from src.utils import format_inr


class WishlistService:
    def get_wishlist(self, user_id: str = "guest_user") -> Dict[str, Any]:
        """Fetch all items saved in user's wishlist."""
        items = []
        if db_manager.is_connected and db_manager.db is not None:
            cursor = db_manager.db.wishlist.find({"user_id": user_id})
            raw_items = list(cursor)
        else:
            raw_items = [
                v for k, v in db_manager.memory_wishlist.items()
                if v.get("user_id") == user_id
            ]
            
        for doc in raw_items:
            pid = doc["product_id"]
            prod = catalog_service.get_product(pid)
            if not prod:
                continue
            items.append({
                "product_id": pid,
                "title": prod["title"],
                "category": prod["category"],
                "price_inr": prod["price_inr"],
                "review_count": prod["review_count"],
                "formatted_price": format_inr(prod["price_inr"])
            })
            
        return {
            "items": items,
            "total_items": len(items)
        }

    def add_to_wishlist(self, product_id: str, user_id: str = "guest_user") -> Dict[str, Any]:
        """Add product to wishlist (idempotent)."""
        prod = catalog_service.get_product(product_id)
        if not prod:
            raise KeyError(f"Product '{product_id}' does not exist.")
            
        if db_manager.is_connected and db_manager.db is not None:
            db_manager.db.wishlist.update_one(
                {"user_id": user_id, "product_id": product_id},
                {"$setOnInsert": {"user_id": user_id, "product_id": product_id}},
                upsert=True
            )
        else:
            key = f"{user_id}:{product_id}"
            db_manager.memory_wishlist[key] = {
                "user_id": user_id,
                "product_id": product_id
            }
            
        return self.get_wishlist(user_id=user_id)

    def remove_from_wishlist(self, product_id: str, user_id: str = "guest_user") -> Dict[str, Any]:
        """Remove product from wishlist."""
        if db_manager.is_connected and db_manager.db is not None:
            db_manager.db.wishlist.delete_one({"user_id": user_id, "product_id": product_id})
        else:
            key = f"{user_id}:{product_id}"
            db_manager.memory_wishlist.pop(key, None)
            
        return self.get_wishlist(user_id=user_id)


wishlist_service = WishlistService()
