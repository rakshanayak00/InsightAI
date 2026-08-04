"""
Product Analytics Utility Module for InsightAI.
Provides product margin analysis, top/bottom product rankers, and category comparisons.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np

def get_product_performance(df: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.DataFrame]:
    """Computes top and bottom products by revenue, profit, and quantity sold."""
    if df.empty or "Product_Name" not in df.columns:
        return {
            "top_revenue": pd.DataFrame(),
            "top_profit": pd.DataFrame(),
            "bottom_profit": pd.DataFrame(),
            "category_summary": pd.DataFrame()
        }

    prod_summary = df.groupby(["Category", "Sub_Category", "Product_Name"]).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()

    prod_summary["Profit_Margin_%"] = np.where(
        prod_summary["Total_Sales"] > 0,
        (prod_summary["Total_Profit"] / prod_summary["Total_Sales"]) * 100,
        0.0
    )

    top_revenue = prod_summary.sort_values(by="Total_Sales", ascending=False).head(top_n)
    top_profit = prod_summary.sort_values(by="Total_Profit", ascending=False).head(top_n)
    bottom_profit = prod_summary.sort_values(by="Total_Profit", ascending=True).head(top_n)

    category_summary = df.groupby("Category").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    category_summary["Margin_%"] = (category_summary["Total_Profit"] / category_summary["Total_Sales"]) * 100

    return {
        "top_revenue": top_revenue,
        "top_profit": top_profit,
        "bottom_profit": bottom_profit,
        "category_summary": category_summary,
        "full_products": prod_summary
    }

def get_discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes impact of discount brackets on average profit margin."""
    if df.empty or "Discount" not in df.columns:
        return pd.DataFrame()

    df_temp = df.copy()
    bins = [-0.01, 0.0, 0.1, 0.2, 0.3, 1.0]
    labels = ["0% (No Discount)", "1-10% Low", "11-20% Moderate", "21-30% High", ">30% Severe"]
    
    df_temp["Discount_Bracket"] = pd.cut(df_temp["Discount"], bins=bins, labels=labels)
    
    impact = df_temp.groupby("Discount_Bracket", observed=False).agg(
        Total_Orders=("Order_ID", "count"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Avg_Profit_Per_Order=("Profit", "mean")
    ).reset_index()
    
    impact["Margin_%"] = np.where(impact["Total_Sales"] > 0, (impact["Total_Profit"] / impact["Total_Sales"]) * 100, 0)
    return impact
