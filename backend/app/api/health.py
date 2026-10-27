"""Health Check API Endpoint."""

from fastapi import APIRouter
from backend.app.db.mongodb import db_manager
from backend.app.services.catalog_service import catalog_service
from backend.app.services.recommendation_service import recommendation_service

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    """System health check endpoint verifying ML model and DB status."""
    return {
        "status": "healthy",
        "service": "E-Commerce Recommendation System API",
        "database": {
            "type": "MongoDB",
            "connected": db_manager.is_connected,
            "mode": "MongoDB Server" if db_manager.is_connected else "In-Memory Fallback"
        },
        "ml_engine": {
            "ready": recommendation_service.recommender.is_ready if recommendation_service.recommender else False,
            "catalog_products": len(catalog_service.df) if catalog_service.df is not None else 0
        }
    }
