"""
Data Loader Utility Module for InsightAI.
Handles data ingestion, schema validation, and realistic sample retail data generation.
"""

import os
from typing import Tuple, List, Optional
import pandas as pd
import numpy as np
from utils.logger import logger

REQUIRED_COLUMNS = [
    "Order_ID", "Order_Date", "Customer_ID", "Customer_Name",
    "Segment", "Region", "Category", "Sub_Category",
    "Product_Name", "Sales", "Quantity", "Discount", "Profit"
]

def generate_sample_dataset(num_records: int = 1500, save_path: Optional[str] = "data/sample_sales_data.csv") -> pd.DataFrame:
    """
    Generates a realistic synthetic retail dataset spanning 2022-2024.
    Includes seasonal trends, varied customer segments, discount impacts, and profitability.
    """
    logger.info(f"Generating synthetic retail sales dataset with {num_records} records...")
    np.random.seed(42)

    # Date range: Jan 1, 2022 to Dec 31, 2024
    start_date = pd.to_datetime("2022-01-01")
    end_date = pd.to_datetime("2024-12-31")
    date_range_days = (end_date - start_date).days
    
    random_days = np.random.randint(0, date_range_days, size=num_records)
    order_dates = start_date + pd.to_timedelta(random_days, unit="D")
    order_dates = np.sort(order_dates)

    # Customers setup
    num_customers = 150
    customer_ids = [f"CUST-{1000 + i}" for i in range(num_customers)]
    customer_names = [f"Customer {i}" for i in range(1, num_customers + 1)]
    cust_map = dict(zip(customer_ids, customer_names))
    
    assigned_cust_ids = np.random.choice(customer_ids, size=num_records)
    assigned_cust_names = [cust_map[cid] for cid in assigned_cust_ids]

    segments = ["Consumer", "Corporate", "Home Office"]
    assigned_segments = np.random.choice(segments, size=num_records, p=[0.5, 0.3, 0.2])

    regions = ["North", "South", "East", "West", "Central"]
    assigned_regions = np.random.choice(regions, size=num_records, p=[0.25, 0.2, 0.25, 0.15, 0.15])

    # Products taxonomy
    catalog = [
        {"Category": "Technology", "Sub_Category": "Laptops", "Product": "Enterprise Laptop Pro 15", "BasePrice": 1200},
        {"Category": "Technology", "Sub_Category": "Phones", "Product": "Smart 5G Phone X", "BasePrice": 800},
        {"Category": "Technology", "Sub_Category": "Monitors", "Product": "UltraWide 34inch Monitor", "BasePrice": 500},
        {"Category": "Technology", "Sub_Category": "Accessories", "Product": "Wireless Noise Cancelling Headset", "BasePrice": 150},
        {"Category": "Furniture", "Sub_Category": "Chairs", "Product": "Ergonomic Executive Chair", "BasePrice": 350},
        {"Category": "Furniture", "Sub_Category": "Tables", "Product": "Standing Height Adjustable Desk", "BasePrice": 600},
        {"Category": "Furniture", "Sub_Category": "Bookcases", "Product": "Modular Oak Bookcase", "BasePrice": 250},
        {"Category": "Office Supplies", "Sub_Category": "Storage", "Product": "Heavy-Duty Archival Boxes", "BasePrice": 45},
        {"Category": "Office Supplies", "Sub_Category": "Binders", "Product": "Premium Leatherette Binder", "BasePrice": 25},
        {"Category": "Office Supplies", "Sub_Category": "Paper", "Product": "Eco-Friendly Recycled Paper Ream", "BasePrice": 15},
    ]

    prod_indices = np.random.randint(0, len(catalog), size=num_records)
    
    categories = [catalog[i]["Category"] for i in prod_indices]
    sub_categories = [catalog[i]["Sub_Category"] for i in prod_indices]
    product_names = [catalog[i]["Product"] for i in prod_indices]
    product_ids = [f"PRD-{100 + i}" for i in prod_indices]
    base_prices = np.array([catalog[i]["BasePrice"] for i in prod_indices], dtype=float)

    # Quantity & Discount logic
    quantities = np.random.randint(1, 8, size=num_records)
    discounts = np.random.choice([0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4], size=num_records, p=[0.4, 0.2, 0.15, 0.1, 0.08, 0.04, 0.03])

    # Seasonal boost logic (higher Q4 sales)
    months = pd.DatetimeIndex(order_dates).month
    seasonal_multiplier = np.where(months >= 10, 1.25, 1.0)

    # Sales calculation
    gross_sales = base_prices * quantities * seasonal_multiplier
    sales = gross_sales * (1.0 - discounts)
    sales = np.round(sales, 2)

    # Profit calculation with discount penalty
    margin = np.where(np.array(categories) == "Technology", 0.35,
             np.where(np.array(categories) == "Furniture", 0.20, 0.25))
    
    # Over-discounting (>25%) penalizes margins severely
    profit = sales * margin - (sales * discounts * 0.5)
    profit = np.round(profit, 2)

    order_ids = [f"ORD-2022-{10000 + i}" for i in range(num_records)]

    df = pd.DataFrame({
        "Order_ID": order_ids,
        "Order_Date": pd.DatetimeIndex(order_dates).strftime("%Y-%m-%d"),
        "Customer_ID": assigned_cust_ids,
        "Customer_Name": assigned_cust_names,
        "Segment": assigned_segments,
        "Country": "United States",
        "Region": assigned_regions,
        "Category": categories,
        "Sub_Category": sub_categories,
        "Product_ID": product_ids,
        "Product_Name": product_names,
        "Sales": sales,
        "Quantity": quantities,
        "Discount": discounts,
        "Profit": profit
    })

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        logger.info(f"Sample dataset saved to {save_path}")

    return df

def validate_dataset(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates if uploaded dataset contains mandatory columns required for BI & Analytics.
    Returns (is_valid, missing_columns).
    """
    df_cols = [c.strip() for c in df.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in df_cols]
    
    if missing:
        logger.warning(f"Dataset validation failed. Missing columns: {missing}")
        return False, missing
    return True, []

def load_data(file_path_or_buffer) -> pd.DataFrame:
    """Loads dataset from file path or Streamlit UploadedFile buffer."""
    if isinstance(file_path_or_buffer, str):
        if file_path_or_buffer.endswith(".csv"):
            df = pd.read_csv(file_path_or_buffer)
        elif file_path_or_buffer.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path_or_buffer)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")
    else:
        # Streamlit UploadedFile
        name = getattr(file_path_or_buffer, "name", "")
        if name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path_or_buffer)
        else:
            df = pd.read_csv(file_path_or_buffer)
            
    df.columns = [c.strip() for c in df.columns]
    return df
