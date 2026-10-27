"""
Product Catalog Service
=======================
Provides in-memory filtered, paginated, and sorted access to the 76,327 products.
"""

import math
import logging
from typing import Dict, List, Optional, Any
import pandas as pd

from src.utils import format_inr
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.categories_summary: List[Dict[str, Any]] = []
        
    def load(self, csv_path: str):
        """Load cleaned product CSV into indexed DataFrame."""
        logger.info(f"Loading product catalog from {csv_path}...")
        self.df = pd.read_csv(csv_path, low_memory=False)
        self.df = self.df.set_index("product_id", drop=False)
        
        # Precompute categories summary
        cat_counts = self.df["category"].value_counts()
        self.categories_summary = [
            {"category": cat, "product_count": int(count)}
            for cat, count in cat_counts.items()
        ]
        logger.info(f"Catalog loaded: {len(self.df):,} products across {len(self.categories_summary)} categories.")
        
    def get_categories(self) -> List[Dict[str, Any]]:
        return self.categories_summary

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Look up single product by product_id in O(1)."""
        pid = str(product_id).strip()
        if self.df is None or pid not in self.df.index:
            return None
        row = self.df.loc[pid]
        return {
            "product_id": pid,
            "title": str(row["title"]),
            "category": str(row["category"]),
            "price_inr": int(row["price_inr"]),
            "price_usd": float(row["price_usd"]),
            "review_count": int(row["review_count"]),
            "source_file": str(row.get("source_file", "")),
            "formatted_price": format_inr(row["price_inr"])
        }

    def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """Filter, sort, and paginate catalog products."""
        if self.df is None:
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
            
        filtered = self.df
        
        # 1. Filter by category
        if category and category.strip() and category.strip().lower() != "all":
            cat_clean = category.strip()
            filtered = filtered[filtered["category"] == cat_clean]
            
        # 2. Filter by search keywords (case-insensitive substring)
        if search and search.strip():
            query = search.strip().lower()
            filtered = filtered[filtered["title"].str.lower().str.contains(query, regex=False)]
            
        # 3. Filter by price range
        if min_price is not None:
            filtered = filtered[filtered["price_inr"] >= min_price]
        if max_price is not None:
            filtered = filtered[filtered["price_inr"] <= max_price]
            
        # 4. Sorting
        if sort_by == "price_asc":
            filtered = filtered.sort_values(by="price_inr", ascending=True)
        elif sort_by == "price_desc":
            filtered = filtered.sort_values(by="price_inr", ascending=False)
        elif sort_by == "reviews_desc":
            filtered = filtered.sort_values(by="review_count", ascending=False)
            
        total_items = len(filtered)
        total_pages = max(1, math.ceil(total_items / page_size))
        current_page = max(1, min(page, total_pages))
        
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_slice = filtered.iloc[start_idx:end_idx]
        
        items = []
        for _, row in page_slice.iterrows():
            items.append({
                "product_id": str(row["product_id"]),
                "title": str(row["title"]),
                "category": str(row["category"]),
                "price_inr": int(row["price_inr"]),
                "price_usd": float(row["price_usd"]),
                "review_count": int(row["review_count"]),
                "source_file": str(row.get("source_file", "")),
                "formatted_price": format_inr(row["price_inr"])
            })
            
        return {
            "items": items,
            "total": total_items,
            "page": current_page,
            "page_size": page_size,
            "total_pages": total_pages
        }


catalog_service = CatalogService()
