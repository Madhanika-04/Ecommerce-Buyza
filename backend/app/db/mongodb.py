"""
MongoDB Database Client and Lifecycle
====================================
Manages PyMongo client connection, index initialization, and graceful fallback.
"""

import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    """Manages the MongoDB connection and collection handles."""
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.is_connected: bool = False
        
        # In-memory storage fallback if MongoDB is temporarily down
        self.memory_cart: Dict[str, Dict[str, Any]] = {}       # key: (user_id, product_id)
        self.memory_wishlist: Dict[str, Dict[str, Any]] = {}   # key: (user_id, product_id)
        self.memory_orders: Dict[str, Dict[str, Any]] = {}     # key: order_id
        
    def connect(self):
        """Establish connection to MongoDB and ensure indexes."""
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            # Ping database to verify connection
            self.client.admin.command("ping")
            self.db = self.client[settings.DATABASE_NAME]
            self.is_connected = True
            logger.info(f"Successfully connected to MongoDB database: '{settings.DATABASE_NAME}'")
            
            # Initialize compound indexes for fast queries & duplicate prevention
            self._init_indexes()
            
        except (ServerSelectionTimeoutError, PyMongoError) as e:
            self.is_connected = False
            logger.warning(
                f"MongoDB connection failed: {e}. "
                "Operating in resilient in-memory mode. Data will persist in memory for the session."
            )
            
    def _init_indexes(self):
        """Create indexes on cart, wishlist, and orders collections."""
        if not self.is_connected or self.db is None:
            return
        try:
            # Cart: Compound index on user_id + product_id
            self.db.cart.create_index(
                [("user_id", ASCENDING), ("product_id", ASCENDING)],
                unique=True,
                name="user_product_unique"
            )
            # Wishlist: Compound index on user_id + product_id
            self.db.wishlist.create_index(
                [("user_id", ASCENDING), ("product_id", ASCENDING)],
                unique=True,
                name="user_product_unique"
            )
            # Orders: Index on user_id and created_at
            self.db.orders.create_index(
                [("user_id", ASCENDING), ("created_at", ASCENDING)],
                name="user_orders_idx"
            )
            logger.info("MongoDB collection indexes initialized successfully.")
        except Exception as e:
            logger.warning(f"Error creating MongoDB indexes: {e}")
            
    def disconnect(self):
        """Close connection cleanly."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("MongoDB connection closed.")


db_manager = MongoDBManager()
