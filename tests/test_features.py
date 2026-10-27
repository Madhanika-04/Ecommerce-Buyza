"""
Unit and Integration Tests for Feature Engineering Pipeline
============================================================
Validates feature text creation, TF-IDF vectorization, sparse representation,
matrix dimensions, and product ID bidirectional mapping.
"""

import os
import json
import pytest
import pandas as pd
import numpy as np
from scipy import sparse
import joblib

from src.features.build_features import (
    clean_feature_text,
    build_product_feature_text,
    FeaturePipeline
)

def test_clean_feature_text():
    """Verify punctuation removal, lowercasing, and whitespace normalization."""
    raw = "  Apple iPhone 15 Pro, 256GB - Titanium (Blue)!!  "
    cleaned = clean_feature_text(raw)
    assert cleaned == "apple iphone 15 pro 256gb titanium blue"


def test_build_product_feature_text():
    """Verify category anchoring and title concatenation."""
    sample_row = pd.Series({
        "category": "Laptops & Computers",
        "title": "Dell XPS 13 Intel Core i7 16GB RAM 512GB SSD"
    })
    doc = build_product_feature_text(sample_row)
    assert "laptops computers" in doc
    assert "dell xps 13" in doc


def test_feature_pipeline_small_corpus():
    """Verify pipeline fit_transform on a controlled mini DataFrame."""
    mini_df = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "category": ["Laptops", "Mobiles", "Laptops"],
        "title": [
            "Apple MacBook Air M2 8GB 256GB",
            "Apple iPhone 14 Pro 128GB",
            "Dell XPS 15 Intel i7 16GB"
        ]
    })
    pipeline = FeaturePipeline(max_features=100, min_df=1)
    matrix = pipeline.fit_transform(mini_df)
    
    assert matrix.shape == (3, len(pipeline.vectorizer.vocabulary_))
    assert pipeline.product_id_to_idx["P1"] == 0
    assert pipeline.product_id_to_idx["P2"] == 1
    assert pipeline.idx_to_product_id[0] == "P1"
    assert sparse.issparse(matrix)


def test_saved_artifacts_integrity():
    """Integration test verifying full artifacts saved on disk."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifacts_dir = os.path.join(project_root, "artifacts")
    
    vec_path = os.path.join(artifacts_dir, "tfidf_vectorizer.joblib")
    matrix_path = os.path.join(artifacts_dir, "tfidf_matrix.npz")
    map_path = os.path.join(artifacts_dir, "product_index_map.joblib")
    meta_path = os.path.join(artifacts_dir, "feature_metadata.json")
    
    assert os.path.exists(vec_path), "Vectorizer artifact missing!"
    assert os.path.exists(matrix_path), "Sparse matrix artifact missing!"
    assert os.path.exists(map_path), "Product index map missing!"
    assert os.path.exists(meta_path), "Feature metadata missing!"
    
    # Load and test matrix
    matrix = sparse.load_npz(matrix_path)
    assert matrix.shape == (76327, 25000), f"Unexpected matrix shape: {matrix.shape}"
    assert matrix.dtype == np.float32
    
    # Load and test mappings
    index_maps = joblib.load(map_path)
    id_to_idx = index_maps["id_to_idx"]
    idx_to_id = index_maps["idx_to_id"]
    
    assert len(id_to_idx) == 76327
    assert len(idx_to_id) == 76327
    assert id_to_idx["IN-PROD-000001"] == 0
    assert idx_to_id[0] == "IN-PROD-000001"
    
    # Bijective check on sample
    for idx in range(100):
        pid = idx_to_id[idx]
        assert id_to_idx[pid] == idx
