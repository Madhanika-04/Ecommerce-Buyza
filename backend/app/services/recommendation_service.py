"""
Recommendation Service
======================
Wraps ContentBasedRecommender singleton for FastAPI requests.
"""

import logging
from typing import List, Dict, Any, Optional

from src.models.recommender import ContentBasedRecommender
from src.utils import format_inr
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        self.recommender: Optional[ContentBasedRecommender] = None
        
    def load(self, artifacts_dir: str, catalog_df_or_path: Any):
        logger.info("Initializing recommendation model for API service...")
        self.recommender = ContentBasedRecommender()
        self.recommender.load(artifacts_dir=artifacts_dir, catalog_path_or_df=catalog_df_or_path)
        logger.info("Recommendation service is ready to serve queries.")
        
    def get_recommendations_for_product(
        self,
        product_id: str,
        top_n: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.recommender or not self.recommender.is_ready:
            raise RuntimeError("Recommendation model is not initialized.")
            
        raw_recs = self.recommender.recommend_by_product_id(
            product_id=product_id,
            top_n=top_n,
            category_filter=category_filter
        )
        
        # Format response with Indian currency
        formatted = []
        for r in raw_recs:
            r_copy = dict(r)
            r_copy["formatted_price"] = format_inr(r["price_inr"])
            formatted.append(r_copy)
        return formatted

    def search_similar_products(
        self,
        query: str,
        top_n: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.recommender or not self.recommender.is_ready:
            raise RuntimeError("Recommendation model is not initialized.")
            
        raw_recs = self.recommender.recommend_by_text(
            query_text=query,
            top_n=top_n,
            category_filter=category_filter
        )
        formatted = []
        for r in raw_recs:
            r_copy = dict(r)
            r_copy["formatted_price"] = format_inr(r["price_inr"])
            formatted.append(r_copy)
        return formatted


recommendation_service = RecommendationService()
