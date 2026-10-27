"""
Shopping Cart Service
=====================
Manages persistent shopping cart items in MongoDB with fallback.
"""

from typing import Dict, List, Any, Optional
from backend.app.db.mongodb import db_manager
from backend.app.services.catalog_service import catalog_service
from src.utils import format_inr


class CartService:
    def get_cart(self, user_id: str = "guest_user") -> Dict[str, Any]:
        """Fetch all items in the user's cart and calculate subtotal/total."""
        items = []
        total_items = 0
        total_inr = 0
        
        if db_manager.is_connected and db_manager.db is not None:
            cursor = db_manager.db.cart.find({"user_id": user_id})
            raw_items = list(cursor)
        else:
            raw_items = [
                v for k, v in db_manager.memory_cart.items()
                if v.get("user_id") == user_id
            ]
            
        for doc in raw_items:
            pid = doc["product_id"]
            qty = int(doc.get("quantity", 1))
            prod = catalog_service.get_product(pid)
            if not prod:
                continue
            price = prod["price_inr"]
            subtotal = price * qty
            total_items += qty
            total_inr += subtotal
            
            items.append({
                "product_id": pid,
                "title": prod["title"],
                "category": prod["category"],
                "price_inr": price,
                "quantity": qty,
                "subtotal_inr": subtotal,
                "formatted_price": format_inr(price),
                "formatted_subtotal": format_inr(subtotal)
            })
            
        return {
            "items": items,
            "total_items": total_items,
            "total_inr": total_inr,
            "formatted_total": format_inr(total_inr)
        }

    def add_to_cart(self, product_id: str, quantity: int = 1, user_id: str = "guest_user") -> Dict[str, Any]:
        """Add product to cart or increment quantity if already present."""
        prod = catalog_service.get_product(product_id)
        if not prod:
            raise KeyError(f"Product '{product_id}' does not exist.")
            
        if db_manager.is_connected and db_manager.db is not None:
            db_manager.db.cart.update_one(
                {"user_id": user_id, "product_id": product_id},
                {"$inc": {"quantity": quantity}},
                upsert=True
            )
        else:
            key = f"{user_id}:{product_id}"
            if key in db_manager.memory_cart:
                db_manager.memory_cart[key]["quantity"] += quantity
            else:
                db_manager.memory_cart[key] = {
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity
                }
                
        return self.get_cart(user_id=user_id)

    def update_quantity(self, product_id: str, quantity: int, user_id: str = "guest_user") -> Dict[str, Any]:
        """Update explicit quantity of a product in the cart."""
        if quantity <= 0:
            return self.remove_from_cart(product_id, user_id=user_id)
            
        if db_manager.is_connected and db_manager.db is not None:
            res = db_manager.db.cart.update_one(
                {"user_id": user_id, "product_id": product_id},
                {"$set": {"quantity": quantity}}
            )
            if res.matched_count == 0:
                raise KeyError(f"Product '{product_id}' is not in the cart.")
        else:
            key = f"{user_id}:{product_id}"
            if key not in db_manager.memory_cart:
                raise KeyError(f"Product '{product_id}' is not in the cart.")
            db_manager.memory_cart[key]["quantity"] = quantity
            
        return self.get_cart(user_id=user_id)

    def remove_from_cart(self, product_id: str, user_id: str = "guest_user") -> Dict[str, Any]:
        """Remove a product from the cart."""
        if db_manager.is_connected and db_manager.db is not None:
            db_manager.db.cart.delete_one({"user_id": user_id, "product_id": product_id})
        else:
            key = f"{user_id}:{product_id}"
            db_manager.memory_cart.pop(key, None)
            
        return self.get_cart(user_id=user_id)

    def clear_cart(self, user_id: str = "guest_user"):
        """Empty the user's cart (e.g. after order checkout)."""
        if db_manager.is_connected and db_manager.db is not None:
            db_manager.db.cart.delete_many({"user_id": user_id})
        else:
            keys_to_remove = [k for k, v in db_manager.memory_cart.items() if v.get("user_id") == user_id]
            for k in keys_to_remove:
                db_manager.memory_cart.pop(k, None)


cart_service = CartService()
