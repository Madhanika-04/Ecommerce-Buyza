"""
Content-Based Recommendation Engine
====================================
Computes real-time, query-specific Cosine Similarity over sparse TF-IDF vectors
for product-to-product and text-to-product recommendations.

Scalability:
Does NOT precompute a dense N x N matrix.
Performs an optimized sparse dot product O(N * K) against the catalog in < 15ms.
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from scipy import sparse
import joblib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.features.build_features import clean_feature_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """
    Production-ready content-based recommendation service using
    sparse TF-IDF feature matrices and Cosine Similarity.
    """
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix: Optional[sparse.csr_matrix] = None
        self.id_to_idx: Dict[str, int] = {}
        self.idx_to_id: Dict[int, str] = {}
        self.catalog_df: Optional[pd.DataFrame] = None
        self.is_ready: bool = False
        
    def load(
        self,
        artifacts_dir: str,
        catalog_path_or_df: Union[str, pd.DataFrame]
    ) -> "ContentBasedRecommender":
        """
        Load model artifacts (sparse matrix, vectorizer, index map) and catalog data.
        """
        start_time = time.time()
        logger.info(f"Loading recommendation engine artifacts from {artifacts_dir}...")
        
        # Load catalog
        if isinstance(catalog_path_or_df, str):
            if not os.path.exists(catalog_path_or_df):
                raise FileNotFoundError(f"Catalog file not found: {catalog_path_or_df}")
            self.catalog_df = pd.read_csv(catalog_path_or_df, low_memory=False)
        else:
            self.catalog_df = catalog_path_or_df.copy()
            
        # Ensure fast O(1) indexed lookup on product_id
        if "product_id" not in self.catalog_df.columns:
            raise ValueError("Catalog must contain a 'product_id' column.")
        self.catalog_df = self.catalog_df.set_index("product_id", drop=False)
        
        # Load Vectorizer
        vec_path = os.path.join(artifacts_dir, "tfidf_vectorizer.joblib")
        if not os.path.exists(vec_path):
            raise FileNotFoundError(f"TF-IDF vectorizer artifact not found: {vec_path}")
        self.vectorizer = joblib.load(vec_path)
        
        # Load Sparse Matrix
        matrix_path = os.path.join(artifacts_dir, "tfidf_matrix.npz")
        if not os.path.exists(matrix_path):
            raise FileNotFoundError(f"Sparse matrix artifact not found: {matrix_path}")
        self.tfidf_matrix = sparse.load_npz(matrix_path)
        
        # Load Index Maps
        map_path = os.path.join(artifacts_dir, "product_index_map.joblib")
        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Index map artifact not found: {map_path}")
        mappings = joblib.load(map_path)
        self.id_to_idx = mappings["id_to_idx"]
        self.idx_to_id = mappings["idx_to_id"]
        
        # Verification
        assert self.tfidf_matrix.shape[0] == len(self.catalog_df), (
            f"Matrix row count ({self.tfidf_matrix.shape[0]}) does not match catalog ({len(self.catalog_df)})"
        )
        self.is_ready = True
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Recommender successfully initialized with {len(self.catalog_df):,} products in {elapsed:.1f}ms.")
        return self

    def recommend_by_product_id(
        self,
        product_id: str,
        top_n: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend Top-N similar products for a currently viewed product.
        
        Guarantees:
        - Query product is strictly excluded from results (no self-recommendations).
        - Results are ordered by descending Cosine Similarity.
        - Scores are strictly in [0.0, 1.0].
        """
        if not self.is_ready:
            raise RuntimeError("Recommender model has not been loaded. Call load() first.")
            
        clean_id = str(product_id).strip()
        if clean_id not in self.id_to_idx:
            raise KeyError(f"Product ID '{clean_id}' not found in catalog.")
            
        query_idx = self.id_to_idx[clean_id]
        
        # Extract query vector (1, K)
        query_vec = self.tfidf_matrix[query_idx]
        
        # Since TfidfVectorizer outputs L2-normalized row vectors,
        # cosine_similarity(A, b) = A . b^T
        similarities = self.tfidf_matrix.dot(query_vec.T).toarray().ravel()
        
        # Strictly exclude the query product itself
        similarities[query_idx] = -1.0
        
        # Optional category filtering
        if category_filter:
            category_mask = (self.catalog_df["category"] == category_filter).values
            similarities[~category_mask] = -1.0
            
        # Top-N selection using argpartition for O(N) efficiency
        n_candidates = min(top_n, len(similarities) - 1)
        if n_candidates <= 0:
            return []
            
        # Get top partition
        partition_indices = np.argpartition(similarities, -n_candidates)[-n_candidates:]
        # Sort top partition in descending order
        sorted_indices = partition_indices[np.argsort(-similarities[partition_indices])]
        
        recommendations = []
        for rank, idx in enumerate(sorted_indices, 1):
            score = float(similarities[idx])
            if score <= 0.0:
                continue  # Skip zero/negative similarity items if catalog has fewer matches
                
            rec_id = self.idx_to_id[idx]
            rec_product = self.catalog_df.loc[rec_id]
            
            recommendations.append({
                "rank": rank,
                "product_id": rec_id,
                "title": str(rec_product["title"]),
                "category": str(rec_product["category"]),
                "price_inr": int(rec_product["price_inr"]),
                "price_usd": float(rec_product["price_usd"]),
                "review_count": int(rec_product["review_count"]),
                "similarity_score": round(max(0.0, min(1.0, score)), 4)
            })
            
        return recommendations

    def recommend_by_text(
        self,
        query_text: str,
        top_n: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend Top-N products matching arbitrary user search text.
        Vectorizes the query and computes Cosine Similarity across catalog.
        """
        if not self.is_ready:
            raise RuntimeError("Recommender model has not been loaded. Call load() first.")
            
        cleaned_text = clean_feature_text(query_text)
        if not cleaned_text:
            return []
            
        # Vectorize query string (1, K)
        query_vec = self.vectorizer.transform([cleaned_text])
        if query_vec.nnz == 0:
            return []  # No vocabulary overlap
            
        # Cosine similarity via sparse dot product
        similarities = self.tfidf_matrix.dot(query_vec.T).toarray().ravel()
        
        if category_filter:
            category_mask = (self.catalog_df["category"] == category_filter).values
            similarities[~category_mask] = -1.0
            
        n_candidates = min(top_n, len(similarities))
        partition_indices = np.argpartition(similarities, -n_candidates)[-n_candidates:]
        sorted_indices = partition_indices[np.argsort(-similarities[partition_indices])]
        
        recommendations = []
        for rank, idx in enumerate(sorted_indices, 1):
            score = float(similarities[idx])
            if score <= 0.001:
                continue
            rec_id = self.idx_to_id[idx]
            rec_product = self.catalog_df.loc[rec_id]
            
            recommendations.append({
                "rank": rank,
                "product_id": rec_id,
                "title": str(rec_product["title"]),
                "category": str(rec_product["category"]),
                "price_inr": int(rec_product["price_inr"]),
                "price_usd": float(rec_product["price_usd"]),
                "review_count": int(rec_product["review_count"]),
                "similarity_score": round(max(0.0, min(1.0, score)), 4)
            })
            
        return recommendations


def get_default_recommender(
    project_root: Optional[str] = None
) -> ContentBasedRecommender:
    """Convenience factory to instantiate and load the singleton recommender."""
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifacts_dir = os.path.join(project_root, "artifacts")
    catalog_path = os.path.join(project_root, "data", "processed", "products_cleaned.csv")
    recommender = ContentBasedRecommender()
    recommender.load(artifacts_dir=artifacts_dir, catalog_path_or_df=catalog_path)
    return recommender
