"""Product and Recommendation Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field

class ProductResponse(BaseModel):
    product_id: str = Field(..., description="Unique product identifier (e.g. IN-PROD-000001)")
    title: str = Field(..., description="Product title and descriptive text")
    category: str = Field(..., description="Standardized retail category")
    price_inr: int = Field(..., description="Price in Indian Rupees (₹)")
    price_usd: float = Field(..., description="Original price in USD")
    review_count: int = Field(..., description="Number of customer reviews")
    source_file: Optional[str] = Field(None, description="Original source dataset file")
    formatted_price: str = Field(..., description="Formatted price string with Indian numbering (e.g. ₹1,299)")


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RecommendationResponse(BaseModel):
    rank: int = Field(..., description="Ranking order (1 being most similar)")
    product_id: str
    title: str
    category: str
    price_inr: int
    price_usd: float
    review_count: int
    similarity_score: float = Field(..., description="Cosine Similarity score between [0.0, 1.0]")
    formatted_price: str


class CategorySummary(BaseModel):
    category: str
    product_count: int
