"""
Feature Engineering Pipeline
=============================
Constructs a unified, normalized text representation combining verified product
attributes (title, category, domain metadata) and fits a TF-IDF Vectorizer
producing a memory-efficient sparse feature matrix.

Scalability Note:
Does NOT compute an O(N^2) dense similarity matrix.
Maintains a sparse CSR matrix and bidirectional ID-to-index mapping for fast
on-demand query cosine similarity calculations.
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def clean_feature_text(text: str) -> str:
    """Preprocess and clean text for TF-IDF vectorization."""
    if not isinstance(text, str):
        return ""
    # Lowercase
    t = text.lower()
    # Replace non-alphanumeric characters with spaces (preserve numbers for specs like 4k, 128gb)
    t = re.sub(r"[^\w\s]", " ", t)
    # Collapse multiple whitespaces
    return re.sub(r"\s+", " ", t).strip()


def build_product_feature_text(row: pd.Series) -> str:
    """
    Construct a unified, category-anchored text document for a product record.
    Incorporates:
    - Category (repeated twice as a semantic anchor to emphasize department relevance)
    - Cleaned Title / Specs
    - Additional attributes if present (actor/director for movies, age for toys)
    """
    category = str(row.get("category", "")).strip()
    title = str(row.get("title", "")).strip()
    
    parts = []
    
    # Category anchor (helps prevent cross-category drift in cosine similarity)
    if category:
        parts.append(f"{category} {category}")
        
    # Product Title & Specs
    if title:
        parts.append(title)
        
    # Extra domain metadata if present
    for extra_field in ["actor", "director", "movie_type", "quality", "age"]:
        val = row.get(extra_field)
        if pd.notna(val) and str(val).strip() and str(val).lower() not in ["nan", "none", "null"]:
            parts.append(str(val).strip())
            
    combined = " ".join(parts)
    return clean_feature_text(combined)


class FeaturePipeline:
    """
    Encapsulates text extraction, TF-IDF vectorization, sparse representation,
    and index mappings.
    """
    def __init__(
        self,
        max_features: int = 25000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        sublinear_tf: bool = True
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.sublinear_tf = sublinear_tf
        
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            sublinear_tf=self.sublinear_tf,
            stop_words="english",
            dtype=np.float32  # Save memory
        )
        self.product_id_to_idx: Dict[str, int] = {}
        self.idx_to_product_id: Dict[int, str] = {}
        self.tfidf_matrix: Optional[sparse.csr_matrix] = None
        
    def fit_transform(self, df: pd.DataFrame) -> sparse.csr_matrix:
        """
        Build text features for all products, fit TF-IDF vectorizer,
        and generate sparse feature matrix.
        """
        logger.info(f"Generating feature text for {len(df):,} products...")
        feature_corpus = df.apply(build_product_feature_text, axis=1).tolist()
        
        logger.info(f"Fitting TfidfVectorizer (max_features={self.max_features}, ngram_range={self.ngram_range})...")
        self.tfidf_matrix = self.vectorizer.fit_transform(feature_corpus)
        
        # Build stable bi-directional mappings
        product_ids = df["product_id"].tolist()
        self.product_id_to_idx = {pid: idx for idx, pid in enumerate(product_ids)}
        self.idx_to_product_id = {idx: pid for idx, pid in enumerate(product_ids)}
        
        sparsity = 1.0 - (self.tfidf_matrix.nnz / (self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1]))
        logger.info(f"TF-IDF Matrix Shape: {self.tfidf_matrix.shape} | Sparsity: {sparsity * 100:.2f}% | Non-zero entries: {self.tfidf_matrix.nnz:,}")
        
        return self.tfidf_matrix
        
    def save_artifacts(self, artifacts_dir: str) -> Dict[str, str]:
        """Save vectorizer, sparse matrix, mappings, and metadata to disk."""
        os.makedirs(artifacts_dir, exist_ok=True)
        
        vec_path = os.path.join(artifacts_dir, "tfidf_vectorizer.joblib")
        matrix_path = os.path.join(artifacts_dir, "tfidf_matrix.npz")
        map_path = os.path.join(artifacts_dir, "product_index_map.joblib")
        meta_path = os.path.join(artifacts_dir, "feature_metadata.json")
        
        logger.info(f"Saving vectorizer to {vec_path}...")
        joblib.dump(self.vectorizer, vec_path, compress=3)
        
        logger.info(f"Saving sparse matrix to {matrix_path}...")
        sparse.save_npz(matrix_path, self.tfidf_matrix)
        
        logger.info(f"Saving index mappings to {map_path}...")
        joblib.dump({
            "id_to_idx": self.product_id_to_idx,
            "idx_to_id": self.idx_to_product_id
        }, map_path, compress=3)
        
        metadata = {
            "num_products": self.tfidf_matrix.shape[0],
            "num_features": self.tfidf_matrix.shape[1],
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "nnz_elements": int(self.tfidf_matrix.nnz),
            "sparsity_pct": round(float(1.0 - (self.tfidf_matrix.nnz / (self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1]))) * 100, 4),
            "ngram_range": list(self.ngram_range),
            "min_df": self.min_df,
            "sublinear_tf": self.sublinear_tf,
            "sample_vocabulary": list(self.vectorizer.get_feature_names_out()[:20])
        }
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Feature engineering artifacts successfully saved to {artifacts_dir}.")
        return {
            "vectorizer": vec_path,
            "matrix": matrix_path,
            "index_map": map_path,
            "metadata": meta_path
        }


def run_feature_pipeline(
    processed_csv_path: str,
    artifacts_dir: str,
    max_features: int = 25000
) -> FeaturePipeline:
    """Orchestrate feature engineering pipeline from cleaned CSV to saved artifacts."""
    logger.info(f"Loading cleaned dataset from {processed_csv_path}...")
    df = pd.read_csv(processed_csv_path, low_memory=False)
    
    pipeline = FeaturePipeline(max_features=max_features)
    pipeline.fit_transform(df)
    pipeline.save_artifacts(artifacts_dir)
    return pipeline


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cleaned_csv = os.path.join(project_root, "data", "processed", "products_cleaned.csv")
    artifacts_directory = os.path.join(project_root, "artifacts")
    
    run_feature_pipeline(
        processed_csv_path=cleaned_csv,
        artifacts_dir=artifacts_directory,
        max_features=25000
    )
