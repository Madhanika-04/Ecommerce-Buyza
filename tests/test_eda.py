"""
Unit and Integration Tests for Exploratory Data Analysis (EDA)
==============================================================
Validates that analytical plots and summary metrics are generated
and match data integrity standards.
"""

import os
import json
import pytest

def test_eda_figures_generated():
    """Verify all 6 publication figures exist and are non-empty."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    figures_dir = os.path.join(project_root, "reports", "figures")
    
    expected_figures = [
        "01_products_by_category.png",
        "02_price_distribution_by_category.png",
        "03_review_counts_distribution.png",
        "04_title_word_count_distribution.png",
        "05_top_brands_frequency.png",
        "06_data_cleaning_funnel.png"
    ]
    
    assert os.path.exists(figures_dir), "Figures directory does not exist!"
    
    for fig_name in expected_figures:
        fig_path = os.path.join(figures_dir, fig_name)
        assert os.path.exists(fig_path), f"Figure {fig_name} was not generated!"
        size = os.path.getsize(fig_path)
        assert size > 10000, f"Figure {fig_name} is too small ({size} bytes), likely corrupted."


def test_eda_summary_json():
    """Verify eda_summary.json contains valid statistical metrics."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    summary_path = os.path.join(project_root, "reports", "eda_summary.json")
    
    assert os.path.exists(summary_path), "eda_summary.json does not exist!"
    
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["total_catalog_size"] == 76327
    assert data["total_categories"] == 9
    assert data["price_stats_inr"]["median"] > 0
    assert data["price_stats_inr"]["mean"] > 0
    assert data["title_stats"]["mean_words"] > 5
    assert len(data["category_price_breakdown"]) == 9
    assert "Laptops & Computers" in data["category_price_breakdown"]
