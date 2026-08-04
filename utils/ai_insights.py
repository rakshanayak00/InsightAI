"""
AI Business Insights Engine for InsightAI Platform.
Analyzes retail dataset patterns and generates structured executive recommendations and risk alerts.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np

def generate_ai_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Evaluates business data heuristics and returns structured recommendation cards.
    Each card dictionary contains: title, type ('opportunity', 'warning', 'risk', 'info'),
    category, message, actionable_recommendation, impact_metric.
    """
    if df.empty:
        return []

    insights = []

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    overall_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

    # 1. Regional Sales & Profit Analysis
    if "Region" in df.columns:
        reg_summary = df.groupby("Region").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        reg_summary["Margin_%"] = (reg_summary["Profit"] / reg_summary["Sales"]) * 100

        top_reg = reg_summary.sort_values(by="Sales", ascending=False).iloc[0]
        bot_reg = reg_summary.sort_values(by="Sales", ascending=True).iloc[0]

        insights.append({
            "title": f"Regional Sales Champion: {top_reg['Region']} Region",
            "type": "opportunity",
            "category": "Regional Expansion",
            "message": f"The {top_reg['Region']} region generates the highest revenue at ${top_reg['Sales']:,.2f} with a profit margin of {top_reg['Margin_%']:.1f}%.",
            "recommendation": f"Increase marketing allocation by 15% in {top_reg['Region']} to double down on winning demand channels.",
            "metric": f"${top_reg['Sales']:,.0f} Revenue"
        })

        if bot_reg["Sales"] < (top_reg["Sales"] * 0.5):
            insights.append({
                "title": f"Regional Underperformance Alert: {bot_reg['Region']}",
                "type": "warning",
                "category": "Regional Optimization",
                "message": f"The {bot_reg['Region']} region accounts for only ${bot_reg['Sales']:,.2f} ({bot_reg['Sales']/total_sales*100:.1f}% of total company sales).",
                "recommendation": f"Conduct local market research or partner with regional distributors to improve distribution efficiency in {bot_reg['Region']}.",
                "metric": f"${bot_reg['Sales']:,.0f} Sales"
            })

    # 2. Category Profitability Analysis
    if "Category" in df.columns:
        cat_summary = df.groupby("Category").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        cat_summary["Margin_%"] = (cat_summary["Profit"] / cat_summary["Sales"]) * 100

        top_cat = cat_summary.sort_values(by="Margin_%", ascending=False).iloc[0]
        bot_cat = cat_summary.sort_values(by="Margin_%", ascending=True).iloc[0]

        insights.append({
            "title": f"High-Margin Leader: {top_cat['Category']}",
            "type": "opportunity",
            "category": "Category Strategy",
            "message": f"{top_cat['Category']} achieves the highest profit margin of {top_cat['Margin_%']:.1f}%, generating ${top_cat['Profit']:,.2f} in net profit.",
            "recommendation": f"Prioritize inventory stocking and promotional bundles for {top_cat['Category']} items to optimize overall margin mix.",
            "metric": f"{top_cat['Margin_%']:.1f}% Margin"
        })

        if bot_cat["Margin_%"] < 15:
            insights.append({
                "title": f"Low Margin Warning: {bot_cat['Category']}",
                "type": "risk",
                "category": "Profit Protection",
                "message": f"{bot_cat['Category']} has a compressed margin of {bot_cat['Margin_%']:.1f}%, significantly below company average ({overall_margin:.1f}%).",
                "recommendation": f"Review supplier vendor pricing and reduce aggressive discount allowances on {bot_cat['Category']}.",
                "metric": f"{bot_cat['Margin_%']:.1f}% Margin"
            })

    # 3. Discount Elasticity & Erosion Risk
    if "Discount" in df.columns:
        high_disc = df[df["Discount"] >= 0.25]
        if not high_disc.empty:
            high_disc_sales = high_disc["Sales"].sum()
            high_disc_profit = high_disc["Profit"].sum()
            high_disc_margin = (high_disc_profit / high_disc_sales * 100) if high_disc_sales > 0 else 0

            if high_disc_margin < 10:
                insights.append({
                    "title": "Severe Margin Erosion from Over-Discounting",
                    "type": "risk",
                    "category": "Pricing Strategy",
                    "message": f"Orders discounted by >=25% generate ${high_disc_sales:,.2f} in sales but yield a low profit margin of only {high_disc_margin:.1f}%.",
                    "recommendation": "Implement strict discount approval caps (max 20%) to prevent value-destructive discounting.",
                    "metric": f"${high_disc_profit:,.0f} Profit"
                })

    # 4. Product Pareto Analysis (80/20 Rule)
    if "Product_Name" in df.columns:
        prod_sales = df.groupby("Product_Name")["Sales"].sum().sort_values(ascending=False)
        cumulative_sales = prod_sales.cumsum() / total_sales
        top_20_pct_count = int(np.ceil(len(prod_sales) * 0.2))
        sales_from_top_20 = cumulative_sales.iloc[top_20_pct_count - 1] * 100 if top_20_pct_count > 0 else 0

        insights.append({
            "title": f"Product Revenue Concentration ({sales_from_top_20:.0f}% Pareto Rule)",
            "type": "info",
            "category": "Portfolio Risk",
            "message": f"The top 20% of products ({top_20_pct_count} items) drive {sales_from_top_20:.1f}% of total company sales revenue.",
            "recommendation": "Ensure guaranteed supply chain availability for these key revenue driver products to mitigate stockout risks.",
            "metric": f"{sales_from_top_20:.0f}% Sales Share"
        })

    # 5. Seasonal Growth Trends
    if "Order_Date" in df.columns:
        df_temp = df.copy()
        df_temp["Order_Date"] = pd.to_datetime(df_temp["Order_Date"])
        df_temp["Month"] = df_temp["Order_Date"].dt.month
        q4_sales = df_temp[df_temp["Month"].isin([10, 11, 12])]["Sales"].sum()
        q4_share = (q4_sales / total_sales * 100) if total_sales > 0 else 0

        if q4_share > 30:
            insights.append({
                "title": "Strong Q4 Holiday Seasonality Detected",
                "type": "opportunity",
                "category": "Seasonal Planning",
                "message": f"Fourth Quarter (Oct-Dec) represents {q4_share:.1f}% of total annual sales, indicating strong year-end holiday demand peaks.",
                "recommendation": "Prepare Q4 inventory stock levels 60 days in advance (by August) and ramp up seasonal marketing campaigns.",
                "metric": f"{q4_share:.1f}% Q4 Share"
            })

    return insights
