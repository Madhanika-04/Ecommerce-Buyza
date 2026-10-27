"""
Data Cleaning and Preprocessing Pipeline
=========================================
Processes raw category CSVs from data/raw/ into a standardized, cleaned catalog
saved in data/processed/products_cleaned.csv.

Handles:
- latin1 character decoding
- Column normalization across varying category schemas
- Removal of stray artifact columns (Unnamed: X)
- Price parsing (USD extraction and Indian Rupee ₹ INR conversion)
- Missing price handling (strict filtering - no zero replacement)
- Review count integer normalization
- Deduplication of identical product listings
- Deterministic product ID generation
- Category injection and text normalization
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Standard exchange rate: 1 USD ~ 83 INR
DEFAULT_USD_TO_INR_RATE = 83.0

# Mapping raw CSV filenames to clean, localized category titles
CATEGORY_MAP: Dict[str, str] = {
    "amazon_audio_video.csv": "Audio & Video",
    "amazon_camra.csv": "Cameras & Photography",
    "amazon_car_accessories.csv": "Automotive & Car Accessories",
    "amazon_laptop.csv": "Laptops & Computers",
    "amazon_men.csv": "Men's Fashion",
    "amazon_men_shoe.csv": "Men's Footwear",
    "amazon_mobile.csv": "Mobiles & Tablets",
    "amazon_movies.csv": "Movies & Entertainment",
    "amazon_toys_1.csv": "Toys & Games",
}


def normalize_column_name(col: str) -> str:
    """Normalize a raw CSV column name to a clean, lowercase snake_case identifier."""
    c = col.strip()
    # Normalize common known variations
    if re.search(r"product.*desc|production.*desc", c, re.IGNORECASE):
        return "raw_title"
    if re.search(r"^price.*dollar", c, re.IGNORECASE):
        return "raw_price_usd"
    if re.search(r"real\s*price.*dollar", c, re.IGNORECASE):
        return "raw_real_price_usd"
    if re.search(r"number.*review", c, re.IGNORECASE):
        return "raw_review_count"
    if re.search(r"free\s*days", c, re.IGNORECASE):
        return "free_days"
    if re.search(r"shipment", c, re.IGNORECASE):
        return "shipment"
    if re.search(r"delivery\s*date", c, re.IGNORECASE):
        return "delivery_date"
    if re.search(r"how\s*many\s*sell", c, re.IGNORECASE):
        return "sales_velocity"
    if re.search(r"stock\s*update", c, re.IGNORECASE):
        return "stock_status"
    return re.sub(r"[^\w]+", "_", c.lower()).strip("_")


def clean_price_series(series: pd.Series) -> pd.Series:
    """
    Extract numeric USD price from raw string/numeric values.
    Removes currency symbols, commas, and strips whitespace.
    Returns float series with NaN for invalid or missing prices.
    """
    cleaned = (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    # Convert non-numeric or malformed strings to NaN
    return pd.to_numeric(cleaned, errors="coerce")


def clean_review_count_series(series: pd.Series) -> pd.Series:
    """
    Parse customer review counts into clean integers.
    Removes commas and formats missing values as 0.
    """
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    numeric = pd.to_numeric(cleaned, errors="coerce")
    return numeric.fillna(0).astype(int)


def clean_text_field(series: pd.Series) -> pd.Series:
    """
    Normalize product text:
    - Replace Windows/latin1 non-breaking spaces and artifact characters
    - Collapse repeated whitespace
    - Strip leading/trailing punctuation
    """
    return (
        series.astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip(" \t\n\r\"'#*-_")
    )


def process_single_csv(
    filepath: str,
    category_name: str,
    usd_to_inr: float = DEFAULT_USD_TO_INR_RATE
) -> Tuple[pd.DataFrame, Dict]:
    """
    Load and clean a single category CSV file.
    Returns the cleaned DataFrame and a telemetry dictionary documenting cleaning counts.
    """
    filename = os.path.basename(filepath)
    logger.info(f"Processing {filename} (Category: {category_name})...")
    
    # Step 1: Read raw CSV using latin1 to handle byte characters
    df_raw = pd.read_csv(filepath, encoding="latin1", on_bad_lines="skip", low_memory=False)
    raw_count = len(df_raw)
    
    # Step 2: Normalize column names
    col_mapping = {col: normalize_column_name(col) for col in df_raw.columns}
    df = df_raw.rename(columns=col_mapping).copy()
    
    # Drop unnamed artifact columns (e.g., Unnamed: 7 through 15)
    cols_to_keep = [c for c in df.columns if not c.startswith("unnamed")]
    df = df[cols_to_keep]
    
    # Step 3: Validate title presence
    if "raw_title" not in df.columns:
        raise ValueError(f"Required title column not identified in {filename}. Available: {df.columns.tolist()}")
        
    df["title"] = clean_text_field(df["raw_title"])
    # Discard empty, corrupted, or placeholder titles
    valid_title_mask = (df["title"].str.len() >= 5) & (~df["title"].isin(["nan", "None", "null", ""]))
    title_dropped = raw_count - int(valid_title_mask.sum())
    df = df[valid_title_mask].copy()
    
    # Step 4: Clean price and convert to INR
    if "raw_price_usd" in df.columns:
        df["price_usd"] = clean_price_series(df["raw_price_usd"])
    else:
        df["price_usd"] = np.nan
        
    # Strictly filter out missing prices: per requirements, never replace with 0 or fabricate
    valid_price_mask = df["price_usd"].notna() & (df["price_usd"] > 0)
    missing_price_dropped = len(df) - int(valid_price_mask.sum())
    df = df[valid_price_mask].copy()
    
    # Compute INR price (rounded to whole integer rupees, typical for Indian retail)
    df["price_inr"] = (df["price_usd"] * usd_to_inr).round(0).astype(int)
    
    # Real price (MSRP/Original Price) if available
    if "raw_real_price_usd" in df.columns:
        real_usd = clean_price_series(df["raw_real_price_usd"])
        df["real_price_inr"] = (real_usd * usd_to_inr).round(0)
    else:
        df["real_price_inr"] = np.nan
        
    # Step 5: Clean review count
    if "raw_review_count" in df.columns:
        df["review_count"] = clean_review_count_series(df["raw_review_count"])
    else:
        df["review_count"] = 0
        
    # Step 6: Inject Category
    df["category"] = category_name
    df["source_file"] = filename
    
    # Select standardized output fields
    selected_fields = ["title", "category", "price_inr", "price_usd", "review_count", "source_file"]
    
    # Retain optional metadata if present
    for extra_col in ["sales_velocity", "delivery_date", "free_days", "shipment", "quality", "release_year", "actor", "director", "age"]:
        if extra_col in df.columns:
            selected_fields.append(extra_col)
            
    df_clean = df[selected_fields].copy()
    
    stats = {
        "filename": filename,
        "category": category_name,
        "raw_rows": raw_count,
        "title_dropped": title_dropped,
        "missing_price_dropped": missing_price_dropped,
        "clean_rows": len(df_clean)
    }
    logger.info(f"Finished {filename}: {raw_count} raw -> {len(df_clean)} clean rows.")
    return df_clean, stats


def clean_entire_dataset(
    raw_dir: str,
    output_csv_path: str,
    summary_report_path: Optional[str] = None,
    usd_to_inr: float = DEFAULT_USD_TO_INR_RATE
) -> pd.DataFrame:
    """
    Clean all category CSVs, combine them into a single master catalog,
    remove duplicate products, generate validated product IDs, and export.
    """
    all_dfs = []
    file_stats = []
    
    for filename, category_name in CATEGORY_MAP.items():
        filepath = os.path.join(raw_dir, filename)
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}. Skipping.")
            continue
            
        clean_df, stats = process_single_csv(filepath, category_name, usd_to_inr=usd_to_inr)
        all_dfs.append(clean_df)
        file_stats.append(stats)
        
    if not all_dfs:
        raise RuntimeError(f"No CSV files found or processed in {raw_dir}")
        
    combined_df = pd.concat(all_dfs, ignore_index=True)
    initial_combined_count = len(combined_df)
    logger.info(f"Combined total before deduplication: {initial_combined_count} rows.")
    
    # Step 7: Deduplication
    # We deduplicate on (title, category) to preserve genuine multi-category relevance
    # while eliminating identical scrapes of the same product.
    duplicates_count = int(combined_df.duplicated(subset=["title", "category"]).sum())
    combined_df = combined_df.drop_duplicates(subset=["title", "category"], keep="first").reset_index(drop=True)
    post_dedup_count = len(combined_df)
    logger.info(f"Dropped {duplicates_count} duplicate items. Remaining: {post_dedup_count} items.")
    
    # Step 8: Deterministic Product Identifier Validation
    # Format: IN-PROD-000001, IN-PROD-000002...
    combined_df["product_id"] = [f"IN-PROD-{i+1:06d}" for i in range(len(combined_df))]
    
    # Reorder columns to place product_id first
    cols = ["product_id", "title", "category", "price_inr", "price_usd", "review_count", "source_file"]
    other_cols = [c for c in combined_df.columns if c not in cols]
    combined_df = combined_df[cols + other_cols]
    
    # Step 9: Save Cleaned Catalog
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    combined_df.to_csv(output_csv_path, index=False, encoding="utf-8")
    logger.info(f"Saved cleaned catalog to {output_csv_path} ({len(combined_df)} records).")
    
    # Step 10: Export cleaning summary telemetry
    summary_report = {
        "raw_total_records": sum(s["raw_rows"] for s in file_stats),
        "post_clean_before_dedup": initial_combined_count,
        "duplicates_removed": duplicates_count,
        "final_cleaned_records": post_dedup_count,
        "currency": "INR (₹)",
        "usd_to_inr_exchange_rate": usd_to_inr,
        "categories_count": combined_df["category"].nunique(),
        "categories": combined_df["category"].value_counts().to_dict(),
        "file_breakdown": file_stats
    }
    
    if summary_report_path:
        os.makedirs(os.path.dirname(summary_report_path), exist_ok=True)
        with open(summary_report_path, "w", encoding="utf-8") as f:
            json.dump(summary_report, f, indent=2)
        logger.info(f"Saved cleaning summary report to {summary_report_path}")
        
    return combined_df


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_directory = os.path.join(project_root, "data", "raw")
    output_file = os.path.join(project_root, "data", "processed", "products_cleaned.csv")
    summary_file = os.path.join(project_root, "reports", "cleaning_summary.json")
    
    clean_entire_dataset(
        raw_dir=raw_directory,
        output_csv_path=output_file,
        summary_report_path=summary_file
    )
