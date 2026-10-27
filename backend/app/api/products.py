"""Products, Search, and Recommendation API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.schemas.product import ProductResponse, ProductListResponse, RecommendationResponse
from backend.app.services.catalog_service import catalog_service
from backend.app.services.recommendation_service import recommendation_service

router = APIRouter()

@router.get("/products", response_model=ProductListResponse, tags=["Catalog"])
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    search: Optional[str] = Query(None, description="Substring search term in title"),
    sort_by: Optional[str] = Query(None, pattern="^(price_asc|price_desc|reviews_desc)$", description="Sort criteria"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price in INR"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price in INR")
):
    """Retrieve filtered, sorted, and paginated product catalog."""
    return catalog_service.list_products(
        page=page,
        page_size=page_size,
        category=category,
        search=search,
        sort_by=sort_by,
        min_price=min_price,
        max_price=max_price
    )


@router.get("/search", response_model=List[RecommendationResponse], tags=["Catalog"])
def semantic_search(
    q: str = Query(..., min_length=2, description="Search query keywords"),
    top_n: int = Query(12, ge=1, le=50, description="Number of results to return"),
    category: Optional[str] = Query(None, description="Optional category filter")
):
    """
    Search products using TF-IDF text vectorization and Cosine Similarity.
    Ranks matching products based on semantic similarity.
    """
    recs = recommendation_service.search_similar_products(
        query=q,
        top_n=top_n,
        category_filter=category
    )
    return recs


@router.get("/products/{product_id}", response_model=ProductResponse, tags=["Catalog"])
def get_product_details(
    product_id: str = Path(..., description="Unique product identifier (e.g. IN-PROD-000001)")
):
    """Retrieve full product details for a given product_id."""
    prod = catalog_service.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")
    return prod


@router.get("/products/{product_id}/recommendations", response_model=List[RecommendationResponse], tags=["Recommendations"])
def get_product_recommendations(
    product_id: str = Path(..., description="Currently viewed product identifier"),
    top_n: int = Query(6, ge=1, le=24, description="Number of similar products to recommend"),
    category: Optional[str] = Query(None, description="Optional category restriction")
):
    """
    Compute real-time Top-N similar products using Content-Based Filtering
    (Sparse TF-IDF + Cosine Similarity). The viewed product is strictly excluded.
    """
    # Verify product exists
    prod = catalog_service.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' does not exist.")
        
    try:
        recs = recommendation_service.get_recommendations_for_product(
            product_id=product_id,
            top_n=top_n,
            category_filter=category
        )
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")
