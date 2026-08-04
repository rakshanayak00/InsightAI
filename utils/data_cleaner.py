"""
Data Cleaner Utility Module for InsightAI.
Provides automated & interactive dataset hygiene routines.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from utils.logger import logger

def get_data_health_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes dataset quality metrics including null counts, duplicates, memory usage."""
    null_counts = df.isnull().sum().to_dict()
    total_nulls = df.isnull().sum().sum()
    duplicate_count = int(df.duplicated().sum())
    
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "total_nulls": total_nulls,
        "null_counts": null_counts,
        "duplicate_rows": duplicate_count,
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    }

def clean_dataset(
    df: pd.DataFrame,
    date_col: str = "Order_Date",
    numeric_cols: Tuple[str, ...] = ("Sales", "Quantity", "Discount", "Profit"),
    null_strategy: str = "impute",
    drop_duplicates: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans dataset by parsing date columns, typecasting numeric columns,
    handling missing values, and dropping duplicates.
    """
    logger.info("Initiating dataset cleaning sequence...")
    df_clean = df.copy()

    # 1. Drop duplicates
    initial_rows = len(df_clean)
    if drop_duplicates:
        df_clean = df_clean.drop_duplicates()
        dropped_dups = initial_rows - len(df_clean)
    else:
        dropped_dups = 0

    # 2. Date conversion
    if date_col in df_clean.columns:
        df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors="coerce")
        # Drop rows with unparseable invalid dates
        df_clean = df_clean.dropna(subset=[date_col])

    # 3. Numeric conversion & null handling
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            
            if df_clean[col].isnull().any():
                if null_strategy == "impute":
                    fill_val = df_clean[col].median()
                    df_clean[col] = df_clean[col].fillna(fill_val)
                elif null_strategy == "drop":
                    df_clean = df_clean.dropna(subset=[col])
                elif null_strategy == "zero":
                    df_clean[col] = df_clean[col].fillna(0)

    # 4. Text column trimming
    str_cols = df_clean.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()

    final_health = get_data_health_summary(df_clean)
    final_health["dropped_duplicates"] = dropped_dups
    logger.info(f"Cleaning completed. Remaining rows: {len(df_clean)}")

    return df_clean, final_health
