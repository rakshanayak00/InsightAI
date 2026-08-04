"""
EDA & Key Performance Indicators (KPIs) Calculator Module for InsightAI.
Provides summary metrics, time series aggregations, and business health indicators.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates core business executive KPIs."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "profit_margin": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "aov": 0.0,
            "rev_growth_mom": 0.0
        }

    total_revenue = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    total_orders = int(df["Order_ID"].nunique() if "Order_ID" in df.columns else len(df))
    total_customers = int(df["Customer_ID"].nunique() if "Customer_ID" in df.columns else 0)
    aov = (total_revenue / total_orders) if total_orders > 0 else 0.0

    # Calculate MoM Revenue Growth if date column exists
    rev_growth_mom = 0.0
    if "Order_Date" in df.columns:
        df_temp = df.copy()
        df_temp["Order_Date"] = pd.to_datetime(df_temp["Order_Date"])
        monthly = df_temp.set_index("Order_Date").resample("ME")["Sales"].sum()
        if len(monthly) >= 2 and monthly.iloc[-2] > 0:
            rev_growth_mom = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "aov": round(aov, 2),
        "rev_growth_mom": round(rev_growth_mom, 2)
    }

def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates sales and profit by month for time-series charts."""
    if df.empty or "Order_Date" not in df.columns:
        return pd.DataFrame()

    df_temp = df.copy()
    df_temp["Order_Date"] = pd.to_datetime(df_temp["Order_Date"])
    monthly = df_temp.groupby(pd.Grouper(key="Order_Date", freq="ME")).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique")
    ).reset_index()

    monthly["Margin_%"] = np.where(monthly["Revenue"] > 0, (monthly["Profit"] / monthly["Revenue"]) * 100, 0)
    return monthly
