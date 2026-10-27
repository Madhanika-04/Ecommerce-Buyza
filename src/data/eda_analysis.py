"""
Exploratory Data Analysis (EDA) Module
=======================================
Analyzes catalog distributions, price characteristics, review metrics,
text lengths, and brand occurrences based on real data.
Saves publication-quality figures to reports/figures/ and summary stats to reports/eda_summary.json.
"""

import os
import re
import json
import logging
from typing import Dict, Any
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Modern theme styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.autolayout"] = True


def extract_potential_brand(title: str) -> str:
    """Extract likely brand name from the first 1-2 words of product title."""
    clean = re.sub(r"^[^\w]+", "", title.strip())
    tokens = clean.split()
    if not tokens:
        return "Unknown"
    first = tokens[0].capitalize()
    # Handle known multi-word brands
    if len(tokens) >= 2:
        two_words = f"{tokens[0]} {tokens[1]}".title()
        if two_words in ["One Plus", "Oneplus", "Paul Smith", "Under Armour", "New Balance", "Polo Ralph"]:
            return two_words
    return first


def generate_eda_figures(
    processed_csv_path: str,
    raw_summary_path: str,
    output_dir: str,
    summary_output_path: str
) -> Dict[str, Any]:
    """Generate all analytical plots and export EDA metrics summary."""
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Loading cleaned dataset from {processed_csv_path}...")
    df = pd.read_csv(processed_csv_path, low_memory=False)
    
    # 1. Product Counts by Category
    logger.info("Generating Figure 1: Products by Category...")
    fig, ax = plt.subplots(figsize=(10, 6))
    category_counts = df["category"].value_counts()
    palette = sns.color_palette("mako", len(category_counts))
    sns.barplot(x=category_counts.values, y=category_counts.index, hue=category_counts.index, palette=palette, legend=False, ax=ax)
    ax.set_title("Product Catalog Distribution by Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Verified Products", fontsize=11)
    ax.set_ylabel("Category", fontsize=11)
    for i, v in enumerate(category_counts.values):
        ax.text(v + 150, i, f"{v:,}", va="center", fontsize=10, fontweight="medium")
    plt.tight_layout()
    fig1_path = os.path.join(output_dir, "01_products_by_category.png")
    fig.savefig(fig1_path, dpi=300)
    plt.close(fig)
    
    # 2. Price Distribution by Category (Log Scale)
    logger.info("Generating Figure 2: Price Distribution by Category...")
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.boxplot(
        data=df,
        x="price_inr",
        y="category",
        hue="category",
        palette="viridis",
        legend=False,
        showfliers=False,  # Exclude extreme outliers for clean visual IQR comparison
        ax=ax
    )
    ax.set_title("Product Price Distribution (₹ INR) across Categories (Interquartile Range)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Price in Indian Rupees (₹)", fontsize=11)
    ax.set_ylabel("Category", fontsize=11)
    # Format x-axis with comma separators
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"₹{int(x):,}"))
    plt.tight_layout()
    fig2_path = os.path.join(output_dir, "02_price_distribution_by_category.png")
    fig.savefig(fig2_path, dpi=300)
    plt.close(fig)
    
    # 3. Customer Engagement: Review Counts Distribution
    logger.info("Generating Figure 3: Review Counts Distribution...")
    fig, ax = plt.subplots(figsize=(10, 5))
    reviewed_df = df[df["review_count"] > 0]["review_count"]
    log_reviews = np.log10(reviewed_df)
    sns.histplot(log_reviews, bins=40, kde=True, color="#2b5c8f", ax=ax)
    ax.set_title("Distribution of Customer Review Counts (Log10 Transformed)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Log10(Review Count) [1 = 10, 2 = 100, 3 = 1,000, 4 = 10,000, 5 = 100,000]", fontsize=11)
    ax.set_ylabel("Product Count", fontsize=11)
    plt.tight_layout()
    fig3_path = os.path.join(output_dir, "03_review_counts_distribution.png")
    fig.savefig(fig3_path, dpi=300)
    plt.close(fig)
    
    # 4. Product Title Length Analysis (Word Counts)
    logger.info("Generating Figure 4: Title Word Count Distribution...")
    df["title_word_count"] = df["title"].astype(str).apply(lambda t: len(t.split()))
    df["title_char_length"] = df["title"].astype(str).apply(len)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df["title_word_count"], bins=35, kde=True, color="#1b8a5a", ax=ax)
    ax.set_title("Distribution of Product Title Lengths (Word Count)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Word Count per Product Title", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.axvline(df["title_word_count"].median(), color="red", linestyle="--", label=f"Median: {df['title_word_count'].median():.0f} words")
    ax.legend(fontsize=11)
    plt.tight_layout()
    fig4_path = os.path.join(output_dir, "04_title_word_count_distribution.png")
    fig.savefig(fig4_path, dpi=300)
    plt.close(fig)
    
    # 5. Top Brand Occurrences (Extracted from Title Tokenization)
    logger.info("Generating Figure 5: Top Brands Frequency...")
    df["brand_token"] = df["title"].apply(extract_potential_brand)
    # Exclude common non-brand generic starting words
    generic_words = {"The", "A", "An", "Set", "Pack", "New", "All", "Men", "Women", "Boys", "Girls", "Kids"}
    filtered_brands = df[~df["brand_token"].isin(generic_words)]["brand_token"].value_counts().head(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=filtered_brands.values, y=filtered_brands.index, hue=filtered_brands.index, palette="crest", legend=False, ax=ax)
    ax.set_title("Top 15 Most Frequent Leading Brand Tokens in Catalog", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Product Count", fontsize=11)
    ax.set_ylabel("Brand / Leading Token", fontsize=11)
    for i, v in enumerate(filtered_brands.values):
        ax.text(v + 10, i, f"{v:,}", va="center", fontsize=9)
    plt.tight_layout()
    fig5_path = os.path.join(output_dir, "05_top_brands_frequency.png")
    fig.savefig(fig5_path, dpi=300)
    plt.close(fig)
    
    # 6. Cleaning Funnel: Raw vs Filtered vs Deduplicated
    logger.info("Generating Figure 6: Data Cleaning Funnel...")
    with open(raw_summary_path, "r", encoding="utf-8") as f:
        clean_summary = json.load(f)
        
    funnel_stages = ["Raw Ingested", "Valid Price/Title", "Duplicates Pruned", "Final Cleaned"]
    funnel_values = [
        clean_summary["raw_total_records"],
        clean_summary["post_clean_before_dedup"],
        clean_summary["duplicates_removed"],
        clean_summary["final_cleaned_records"]
    ]
    colors = ["#4a5568", "#2b6cb0", "#c53030", "#2f855a"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(funnel_stages, funnel_values, color=colors, width=0.55)
    ax.set_title("Data Cleaning and Deduplication Funnel", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Number of Records", fontsize=11)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, height + 1000, f"{int(height):,}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(funnel_values) * 1.15)
    plt.tight_layout()
    fig6_path = os.path.join(output_dir, "06_data_cleaning_funnel.png")
    fig.savefig(fig6_path, dpi=300)
    plt.close(fig)
    
    # Summary Statistics Compilation
    price_by_cat = df.groupby("category")["price_inr"].agg(["count", "mean", "median", "min", "max", "std"]).round(2).to_dict(orient="index")
    
    eda_stats = {
        "total_catalog_size": len(df),
        "total_categories": df["category"].nunique(),
        "price_stats_inr": {
            "mean": round(float(df["price_inr"].mean()), 2),
            "median": round(float(df["price_inr"].median()), 2),
            "min": int(df["price_inr"].min()),
            "max": int(df["price_inr"].max()),
            "std": round(float(df["price_inr"].std()), 2)
        },
        "review_stats": {
            "mean_reviews": round(float(df["review_count"].mean()), 2),
            "median_reviews": round(float(df["review_count"].median()), 2),
            "max_reviews": int(df["review_count"].max()),
            "products_with_reviews_pct": round(float((df["review_count"] > 0).mean() * 100), 2)
        },
        "title_stats": {
            "mean_words": round(float(df["title_word_count"].mean()), 2),
            "median_words": round(float(df["title_word_count"].median()), 2),
            "min_words": int(df["title_word_count"].min()),
            "max_words": int(df["title_word_count"].max()),
            "mean_characters": round(float(df["title_char_length"].mean()), 2)
        },
        "category_price_breakdown": price_by_cat,
        "figures_generated": [
            "01_products_by_category.png",
            "02_price_distribution_by_category.png",
            "03_review_counts_distribution.png",
            "04_title_word_count_distribution.png",
            "05_top_brands_frequency.png",
            "06_data_cleaning_funnel.png"
        ]
    }
    
    with open(summary_output_path, "w", encoding="utf-8") as f:
        json.dump(eda_stats, f, indent=2)
    logger.info(f"Saved EDA statistical summary to {summary_output_path}")
    
    return eda_stats


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_path = os.path.join(project_root, "data", "processed", "products_cleaned.csv")
    cleaning_summary_path = os.path.join(project_root, "reports", "cleaning_summary.json")
    figures_dir = os.path.join(project_root, "reports", "figures")
    eda_summary_path = os.path.join(project_root, "reports", "eda_summary.json")
    
    generate_eda_figures(
        processed_csv_path=processed_path,
        raw_summary_path=cleaning_summary_path,
        output_dir=figures_dir,
        summary_output_path=eda_summary_path
    )
