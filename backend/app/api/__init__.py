"""API routers package."""
from fastapi import APIRouter
from .health import router as health_router
from .categories import router as categories_router
from .products import router as products_router
from .cart import router as cart_router
from .wishlist import router as wishlist_router
from .orders import router as orders_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(categories_router)
api_router.include_router(products_router)
api_router.include_router(cart_router)
api_router.include_router(wishlist_router)
api_router.include_router(orders_router)
