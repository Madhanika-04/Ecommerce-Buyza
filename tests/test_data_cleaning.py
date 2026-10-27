"""
Unit and Integration Tests for Data Cleaning Pipeline
======================================================
Tests verify schema normalization, missing value handling,
price conversion, duplicate elimination, and ID generation.
"""

import os
import pytest
import pandas as pd
import numpy as np

from src.data.clean_dataset import (
    normalize_column_name,
    clean_price_series,
    clean_review_count_series,
    clean_text_field,
    clean_entire_dataset,
    DEFAULT_USD_TO_INR_RATE
)

def test_normalize_column_name():
    """Verify mismatched and typo-laden raw columns map to standardized names."""
    assert normalize_column_name("Product Description ") == "raw_title"
    assert normalize_column_name("Production Description") == "raw_title"
    assert normalize_column_name("Price(Dollar)") == "raw_price_usd"
    assert normalize_column_name("PriceDollar)") == "raw_price_usd"
    assert normalize_column_name("Real price(Dollar)") == "raw_real_price_usd"
    assert normalize_column_name("Number of  reviews") == "raw_review_count"
    assert normalize_column_name("Number of reviews") == "raw_review_count"
    assert normalize_column_name("How many sell  in past month") == "sales_velocity"


def test_clean_price_series():
    """Verify currency symbols, commas, and invalid values are parsed accurately."""
    raw_prices = pd.Series(["$12.50", "1,299.00", "25", "invalid_string", None, "   $99   "])
    cleaned = clean_price_series(raw_prices)
    
    assert cleaned.iloc[0] == 12.50
    assert cleaned.iloc[1] == 1299.00
    assert cleaned.iloc[2] == 25.0
    assert np.isnan(cleaned.iloc[3])  # Invalid text must become NaN, never 0
    assert np.isnan(cleaned.iloc[4])  # Missing must become NaN, never 0
    assert cleaned.iloc[5] == 99.0


def test_clean_review_count_series():
    """Verify review counts handle commas, whitespace, and convert missing to 0."""
    raw_reviews = pd.Series(["82,773", " 500 ", "1,234,567", None, "invalid"])
    cleaned = clean_review_count_series(raw_reviews)
    
    assert cleaned.iloc[0] == 82773
    assert cleaned.iloc[1] == 500
    assert cleaned.iloc[2] == 1234567
    assert cleaned.iloc[3] == 0
    assert cleaned.iloc[4] == 0


def test_clean_text_field():
    """Verify whitespace collapsing and punctuation stripping."""
    raw_titles = pd.Series([
        "  Samsung Galaxy   S23   Ultra  ",
        "\"Apple iPhone 15 Pro Max\"*",
        "HP Pavilion Laptop   15.6''  "
    ])
    cleaned = clean_text_field(raw_titles)
    
    assert cleaned.iloc[0] == "Samsung Galaxy S23 Ultra"
    assert cleaned.iloc[1] == "Apple iPhone 15 Pro Max"
    assert cleaned.iloc[2] == "HP Pavilion Laptop 15.6"


def test_cleaned_dataset_integrity():
    """Integration test verifying output CSV existence, shape, columns, and constraints."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_csv = os.path.join(project_root, "data", "processed", "products_cleaned.csv")
    
    assert os.path.exists(processed_csv), "products_cleaned.csv does not exist!"
    
    df = pd.read_csv(processed_csv, low_memory=False)
    
    # Check row count > 50,000 genuine records
    assert len(df) > 50000, f"Expected >50,000 clean records, got {len(df)}"
    
    # Check required columns
    required_cols = ["product_id", "title", "category", "price_inr", "price_usd", "review_count", "source_file"]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"
        
    # Check no nulls in mandatory fields
    assert df["product_id"].isnull().sum() == 0, "Nulls found in product_id"
    assert df["title"].isnull().sum() == 0, "Nulls found in title"
    assert df["category"].isnull().sum() == 0, "Nulls found in category"
    assert df["price_inr"].isnull().sum() == 0, "Nulls found in price_inr"
    
    # Check all prices are strictly positive (no 0 or negative prices)
    assert (df["price_inr"] <= 0).sum() == 0, "Found non-positive price_inr values"
    assert (df["price_usd"] <= 0).sum() == 0, "Found non-positive price_usd values"
    
    # Check product_id uniqueness
    assert df["product_id"].nunique() == len(df), "product_id is not unique!"
    
    # Check ID format IN-PROD-XXXXXX
    sample_ids = df["product_id"].head(10).tolist()
    for pid in sample_ids:
        assert pid.startswith("IN-PROD-"), f"Unexpected ID format: {pid}"
        
    # Check categories coverage
    assert df["category"].nunique() == 9, f"Expected 9 categories, got {df['category'].nunique()}"
