"""
Dataset inspection script for Amazon 100k Products dataset.
Examines file sizes, encoding, row counts, columns, data types, missing values, and formatting anomalies.
"""

import os
import json
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

def inspect_all():
    files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith(".csv")])
    print(f"Discovered {len(files)} CSV files in {RAW_DIR}\n")
    
    summary = []
    
    for filename in files:
        filepath = os.path.join(RAW_DIR, filename)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        # Count physical lines
        with open(filepath, "rb") as f:
            physical_lines = sum(1 for _ in f)
            
        # Parse with pandas latin1 and skip bad lines to analyze parser behavior
        try:
            df = pd.read_csv(filepath, encoding="latin1", on_bad_lines="skip", low_memory=False)
            parsed_rows = len(df)
            columns = list(df.columns)
            missing = df.isnull().sum().to_dict()
            dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
            # Detect unnamed columns
            unnamed_cols = [c for c in columns if c.startswith("Unnamed")]
            
            # Check price column variants
            price_cols = [c for c in columns if "price" in c.lower()]
            desc_cols = [c for c in columns if "desc" in c.lower()]
            
            file_report = {
                "filename": filename,
                "size_mb": round(file_size_mb, 2),
                "physical_lines": physical_lines,
                "parsed_rows": parsed_rows,
                "dropped_lines": (physical_lines - 1) - parsed_rows,
                "column_count": len(columns),
                "columns": columns,
                "unnamed_cols_count": len(unnamed_cols),
                "desc_col": desc_cols[0] if desc_cols else None,
                "price_cols": price_cols,
                "missing_summary": missing,
                "sample_row": df.iloc[0].dropna().to_dict() if len(df) > 0 else {}
            }
            summary.append(file_report)
            
            print(f"=== {filename} ===")
            print(f"  Size: {file_size_mb:.2f} MB | Physical Lines: {physical_lines} | Parsed Rows: {parsed_rows}")
            print(f"  Columns ({len(columns)}): {columns}")
            if unnamed_cols:
                print(f"  [Notice] Found {len(unnamed_cols)} unnamed artifact columns: {unnamed_cols}")
            print(f"  Text Column: {desc_cols[0] if desc_cols else 'NOT FOUND'}")
            print(f"  Price Columns: {price_cols}")
            print(f"  Missing values: {missing}")
            print(f"  Sample Product Title: {df.iloc[0][desc_cols[0]] if desc_cols else 'N/A'}")
            print()
            
        except Exception as e:
            print(f"Error parsing {filename}: {e}\n")
            
    # Overall summary
    total_parsed = sum(s["parsed_rows"] for s in summary)
    print("=" * 60)
    print(f"OVERALL SUMMARY: {len(summary)} files parsed successfully.")
    print(f"Total raw product records: {total_parsed:,}")
    print("=" * 60)
    
    return summary

if __name__ == "__main__":
    inspect_all()
