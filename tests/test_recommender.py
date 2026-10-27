"""
Unit and Integration Tests for Recommendation Engine & Evaluation
==================================================================
Tests verify self-recommendation exclusion, score bounds [0.0, 1.0],
top_n limits, category filtering, search recommendations, and error handling.
"""

import os
import json
import pytest
import pandas as pd
from src.models.recommender import ContentBasedRecommender, get_default_recommender

@pytest.fixture(scope="module")
def recommender():
    """Load default trained recommender fixture."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return get_default_recommender(project_root)


def test_recommender_is_ready(recommender):
    """Verify recommender initializes and has non-empty catalog."""
    assert recommender.is_ready is True
    assert len(recommender.catalog_df) == 76327
    assert recommender.tfidf_matrix.shape[0] == 76327


def test_self_recommendation_exclusion(recommender):
    """Verify that a product is never recommended to itself."""
    test_ids = ["IN-PROD-000001", "IN-PROD-001000", "IN-PROD-010000"]
    for pid in test_ids:
        recs = recommender.recommend_by_product_id(pid, top_n=10)
        rec_ids = [r["product_id"] for r in recs]
        assert pid not in rec_ids, f"Self-recommendation detected for {pid}!"


def test_score_range_and_ordering(recommender):
    """Verify scores are bounded in [0.0, 1.0] and sorted in descending order."""
    recs = recommender.recommend_by_product_id("IN-PROD-000001", top_n=5)
    assert len(recs) > 0
    scores = [r["similarity_score"] for r in recs]
    
    for s in scores:
        assert 0.0 <= s <= 1.0, f"Score out of bounds: {s}"
        
    # Check descending sort
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], "Recommendations not sorted in descending order!"


def test_top_n_limits(recommender):
    """Verify requested Top-N count is respected."""
    for n in [1, 3, 7, 10]:
        recs = recommender.recommend_by_product_id("IN-PROD-000001", top_n=n)
        assert len(recs) <= n


def test_invalid_product_id_raises_key_error(recommender):
    """Verify querying an invalid product_id raises KeyError."""
    with pytest.raises(KeyError):
        recommender.recommend_by_product_id("NON_EXISTENT_ID_999999", top_n=5)


def test_category_filter(recommender):
    """Verify that applying category filter strictly restricts recommendations to that category."""
    recs = recommender.recommend_by_product_id(
        "IN-PROD-000001",
        top_n=5,
        category_filter="Cameras & Photography"
    )
    for r in recs:
        assert r["category"] == "Cameras & Photography"


def test_recommend_by_text_search(recommender):
    """Verify free-text semantic query recommendation."""
    recs = recommender.recommend_by_text("wireless bluetooth noise cancelling headphones", top_n=5)
    assert len(recs) > 0
    assert any("headphone" in r["title"].lower() or "speaker" in r["title"].lower() or "bluetooth" in r["title"].lower() for r in recs)


def test_recommendation_evaluation_report():
    """Verify recommendation_evaluation.json contains valid diagnostic findings."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(project_root, "reports", "recommendation_evaluation.json")
    
    assert os.path.exists(report_path), "Evaluation report missing!"
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert report["self_recommendation_rate_pct"] == 0.0, "Self-recommendation rate must be 0%!"
    assert report["duplicate_recommendation_rate_pct"] == 0.0, "Duplicate recommendation rate must be 0%!"
    assert report["latency_ms"]["mean"] < 20.0, f"Mean latency too high: {report['latency_ms']['mean']} ms"
    assert len(report["qualitative_cases"]) >= 4
