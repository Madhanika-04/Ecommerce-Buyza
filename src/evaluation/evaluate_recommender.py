"""
Recommendation Engine Evaluation and Diagnostics
=================================================
Evaluates the unsupervised Content-Based Recommendation system against
crucial operational, statistical, and algorithmic standards:
- Strict Self-Recommendation Exclusion (0% self-recommendation)
- Score Bounds and Distribution Validation (0.0 <= Cosine Similarity <= 1.0)
- Recommendation Uniqueness (0% duplicates)
- Category Cohesion and Department Relevance
- Catalog Coverage
- Query Latency Benchmarking (P50, P95, P99)
- Qualitative Case Studies across major retail categories

Note:
As this is an unsupervised content-based recommendation task without explicit
user clickstream ground-truth, Cosine Similarity represents lexical/semantic
content proximity, NOT classification accuracy.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, List, Any
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.models.recommender import ContentBasedRecommender, get_default_recommender

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_recommender_system(
    recommender: ContentBasedRecommender,
    sample_size: int = 500,
    top_n: int = 5,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Run diagnostic evaluation across a balanced sample of products.
    """
    catalog = recommender.catalog_df
    total_catalog = len(catalog)
    logger.info(f"Starting evaluation across sample of {sample_size} products from catalog of {total_catalog:,}...")
    
    np.random.seed(random_seed)
    # Stratified or balanced sample across available categories
    sample_ids = []
    per_cat = max(10, sample_size // catalog["category"].nunique())
    for cat, group in catalog.groupby("category"):
        sampled_from_cat = group.sample(min(per_cat, len(group)), random_state=random_seed)
        sample_ids.extend(sampled_from_cat["product_id"].tolist())
        
    sample_ids = sample_ids[:sample_size]
    
    latencies = []
    self_rec_count = 0
    duplicate_rec_count = 0
    invalid_score_count = 0
    category_match_count = 0
    total_recommended_items = 0
    all_recommended_ids = set()
    similarity_scores = []
    
    for query_id in sample_ids:
        query_prod = catalog.loc[query_id]
        query_cat = query_prod["category"]
        
        t0 = time.perf_counter()
        recs = recommender.recommend_by_product_id(query_id, top_n=top_n)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed_ms)
        
        rec_ids = [r["product_id"] for r in recs]
        total_recommended_items += len(recs)
        all_recommended_ids.update(rec_ids)
        
        # 1. Self-recommendation check
        if query_id in rec_ids:
            self_rec_count += 1
            
        # 2. Duplicate recommendations check
        if len(rec_ids) != len(set(rec_ids)):
            duplicate_rec_count += 1
            
        # 3. Score bounds and category cohesion
        for r in recs:
            score = r["similarity_score"]
            similarity_scores.append(score)
            if score < 0.0 or score > 1.0:
                invalid_score_count += 1
            if r["category"] == query_cat:
                category_match_count += 1
                
    # Qualitative Case Studies on known target products
    case_study_targets = [
        ("Laptops & Computers", "amazon_laptop.csv"),
        ("Men's Footwear", "amazon_men_shoe.csv"),
        ("Cameras & Photography", "amazon_camra.csv"),
        ("Audio & Video", "amazon_audio_video.csv"),
        ("Mobiles & Tablets", "amazon_mobile.csv")
    ]
    
    qualitative_cases = []
    for cat_name, source in case_study_targets:
        match = catalog[(catalog["category"] == cat_name) & (catalog["source_file"] == source)]
        if len(match) > 0:
            target_id = match.iloc[0]["product_id"]
            target_item = match.iloc[0]
            recs = recommender.recommend_by_product_id(target_id, top_n=3)
            qualitative_cases.append({
                "query_product": {
                    "product_id": target_id,
                    "title": target_item["title"],
                    "category": target_item["category"],
                    "price_inr": int(target_item["price_inr"])
                },
                "recommendations": [
                    {
                        "rank": r["rank"],
                        "product_id": r["product_id"],
                        "title": r["title"],
                        "category": r["category"],
                        "price_inr": r["price_inr"],
                        "similarity_score": r["similarity_score"]
                    } for r in recs
                ]
            })
            
    # Compile Metrics
    coverage_pct = round((len(all_recommended_ids) / total_catalog) * 100.0, 3)
    intra_cat_pct = round((category_match_count / max(1, total_recommended_items)) * 100.0, 2)
    
    report = {
        "evaluation_sample_size": len(sample_ids),
        "requested_top_n": top_n,
        "total_catalog_size": total_catalog,
        "self_recommendation_rate_pct": round((self_rec_count / len(sample_ids)) * 100.0, 4),
        "duplicate_recommendation_rate_pct": round((duplicate_rec_count / len(sample_ids)) * 100.0, 4),
        "score_bounds_validity_pct": round(100.0 - (invalid_score_count / max(1, total_recommended_items) * 100.0), 2),
        "intra_category_cohesion_pct": intra_cat_pct,
        "catalog_coverage_pct": coverage_pct,
        "unique_products_recommended_count": len(all_recommended_ids),
        "similarity_score_stats": {
            "mean": round(float(np.mean(similarity_scores)), 4) if similarity_scores else 0.0,
            "median": round(float(np.median(similarity_scores)), 4) if similarity_scores else 0.0,
            "p25": round(float(np.percentile(similarity_scores, 25)), 4) if similarity_scores else 0.0,
            "p75": round(float(np.percentile(similarity_scores, 75)), 4) if similarity_scores else 0.0,
            "min": round(float(np.min(similarity_scores)), 4) if similarity_scores else 0.0,
            "max": round(float(np.max(similarity_scores)), 4) if similarity_scores else 0.0
        },
        "latency_ms": {
            "mean": round(float(np.mean(latencies)), 2),
            "p50": round(float(np.percentile(latencies, 50)), 2),
            "p95": round(float(np.percentile(latencies, 95)), 2),
            "p99": round(float(np.percentile(latencies, 99)), 2)
        },
        "qualitative_cases": qualitative_cases
    }
    
    logger.info("Evaluation Complete. Results:")
    logger.info(f" - Self-Recommendation Rate: {report['self_recommendation_rate_pct']}% (Target: 0.0%)")
    logger.info(f" - Duplicate Recommendation Rate: {report['duplicate_recommendation_rate_pct']}% (Target: 0.0%)")
    logger.info(f" - Intra-Category Cohesion: {report['intra_category_cohesion_pct']}%")
    logger.info(f" - Mean Latency: {report['latency_ms']['mean']} ms (P95: {report['latency_ms']['p95']} ms)")
    return report


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rec = get_default_recommender(project_root)
    eval_report = evaluate_recommender_system(rec, sample_size=500, top_n=5)
    
    output_path = os.path.join(project_root, "reports", "recommendation_evaluation.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)
    logger.info(f"Evaluation report saved to {output_path}")
