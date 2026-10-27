"""
Order Service & Simulated Checkout
==================================
Simulates order processing, validates Indian addresses and PIN codes,
and saves confirmed orders to MongoDB.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from backend.app.db.mongodb import db_manager
from backend.app.services.cart_service import cart_service
from backend.app.schemas.order import OrderCreate, DeliveryAddress
from src.utils import format_inr


class OrderService:
    def create_simulated_order(self, order_data: OrderCreate) -> Dict[str, Any]:
        """Convert current cart items into a confirmed simulated order."""
        user_id = order_data.user_id or "guest_user"
        cart = cart_service.get_cart(user_id=user_id)
        
        if not cart["items"]:
            raise ValueError("Cannot place order with an empty cart.")
            
        order_id = f"IN-ORD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        order_record = {
            "order_id": order_id,
            "user_id": user_id,
            "items": cart["items"],
            "total_items": cart["total_items"],
            "total_inr": cart["total_inr"],
            "formatted_total": cart["formatted_total"],
            "delivery_address": order_data.delivery_address.model_dump(),
            "payment_method": order_data.payment_method,
            "status": "Confirmed (Simulated)",
            "created_at": created_at
        }
        
        # Save to database
        if db_manager.is_connected and db_manager.db is not None:
            db_manager.db.orders.insert_one(order_record)
        else:
            db_manager.memory_orders[order_id] = order_record
            
        # Empty cart upon successful order creation
        cart_service.clear_cart(user_id=user_id)
        
        return order_record

    def get_user_orders(self, user_id: str = "guest_user") -> List[Dict[str, Any]]:
        """Retrieve historical orders for a user."""
        if db_manager.is_connected and db_manager.db is not None:
            cursor = db_manager.db.orders.find({"user_id": user_id}).sort("created_at", -1)
            orders = list(cursor)
            # Remove MongoDB internal _id before returning
            for o in orders:
                o.pop("_id", None)
            return orders
        else:
            orders = [
                v for k, v in db_manager.memory_orders.items()
                if v.get("user_id") == user_id
            ]
            orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return orders

    def get_order_by_id(self, order_id: str, user_id: str = "guest_user") -> Optional[Dict[str, Any]]:
        """Retrieve single order details."""
        if db_manager.is_connected and db_manager.db is not None:
            order = db_manager.db.orders.find_one({"order_id": order_id, "user_id": user_id})
            if order:
                order.pop("_id", None)
            return order
        else:
            order = db_manager.memory_orders.get(order_id)
            if order and order.get("user_id") == user_id:
                return order
            return None


order_service = OrderService()
