"""Categories API Endpoint."""

from typing import List
from fastapi import APIRouter
from backend.app.schemas.product import CategorySummary
from backend.app.services.catalog_service import catalog_service

router = APIRouter()

@router.get("/categories", response_model=List[CategorySummary], tags=["Catalog"])
def get_categories():
    """Retrieve all available retail categories with product counts."""
    return catalog_service.get_categories()
