"""
Plotly Visualizations Module for InsightAI.
Provides reusable, dark-theme styled interactive charts for BI dashboards & forecasting.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Unified Dark SaaS Color Palette
DARK_LAYOUT = dict(
    paper_bgcolor="rgba(17, 24, 39, 0.0)",
    plot_bgcolor="rgba(17, 24, 39, 0.4)",
    font=dict(family="Inter, sans-serif", color="#F3F4F6", size=12),
    xaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)", showline=True, linecolor="rgba(255, 255, 255, 0.1)"),
    yaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)", showline=True, linecolor="rgba(255, 255, 255, 0.1)"),
    legend=dict(bgcolor="rgba(17, 24, 39, 0.6)", font=dict(color="#D1D5DB")),
    margin=dict(l=40, r=40, t=50, b=40)
)

COLOR_PRIMARY = "#3B82F6"
COLOR_SECONDARY = "#8B5CF6"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_ACCENT = "#06B6D4"

COLOR_SEQUENCE = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4", "#EC4899"]

def plot_monthly_sales_trend(monthly_df: pd.DataFrame) -> go.Figure:
    """Creates a dual-axis Area & Line chart for Monthly Revenue and Profit."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if monthly_df.empty:
        return fig

    fig.add_trace(
        go.Scatter(
            x=monthly_df["Order_Date"], y=monthly_df["Revenue"],
            name="Sales Revenue ($)", mode="lines+markers",
            fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.15)",
            line=dict(color=COLOR_PRIMARY, width=3, shape="spline"),
            marker=dict(size=6)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_df["Order_Date"], y=monthly_df["Profit"],
            name="Net Profit ($)", mode="lines+markers",
            line=dict(color=COLOR_SUCCESS, width=2.5, dash="dot"),
            marker=dict(size=6, symbol="diamond")
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="<b>Monthly Sales Revenue & Net Profit Trend</b>",
        title_font_size=16,
        hovermode="x unified",
        **DARK_LAYOUT
    )
    fig.update_yaxes(title_text="Sales Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Net Profit ($)", secondary_y=True)

    return fig

def plot_category_distribution(df: pd.DataFrame) -> go.Figure:
    """Creates a Donut chart for Sales Share by Category."""
    if df.empty or "Category" not in df.columns:
        return go.Figure()

    cat_df = df.groupby("Category")["Sales"].sum().reset_index()

    fig = px.pie(
        cat_df, values="Sales", names="Category",
        hole=0.55,
        color_discrete_sequence=COLOR_SEQUENCE,
        title="<b>Revenue Share by Category</b>"
    )
    fig.update_traces(
        textposition="inside", textinfo="percent+label",
        marker=dict(line=dict(color="#0B0F19", width=2))
    )
    fig.update_layout(title_font_size=16, **DARK_LAYOUT)
    return fig

def plot_regional_performance(df: pd.DataFrame) -> go.Figure:
    """Creates a Grouped Bar chart for Revenue & Profit by Region."""
    if df.empty or "Region" not in df.columns:
        return go.Figure()

    reg_df = df.groupby("Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values(by="Revenue", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=reg_df["Region"], y=reg_df["Revenue"],
        name="Revenue ($)", marker_color=COLOR_PRIMARY
    ))
    fig.add_trace(go.Bar(
        x=reg_df["Region"], y=reg_df["Profit"],
        name="Profit ($)", marker_color=COLOR_SUCCESS
    ))

    fig.update_layout(
        barmode="group",
        title="<b>Regional Sales & Profit Comparison</b>",
        title_font_size=16,
        xaxis_title="Region", yaxis_title="Amount ($)",
        **DARK_LAYOUT
    )
    return fig

def plot_top_products_bar(top_df: pd.DataFrame, title: str = "Top Products by Revenue") -> go.Figure:
    """Creates a horizontal Bar chart for Top Products."""
    if top_df.empty:
        return go.Figure()

    df_sorted = top_df.sort_values(by="Total_Sales", ascending=True)

    fig = px.bar(
        df_sorted, x="Total_Sales", y="Product_Name",
        orientation="h",
        text=df_sorted["Total_Sales"].apply(lambda v: f"${v:,.0f}"),
        color="Total_Profit",
        color_continuous_scale="Blues",
        title=f"<b>{title}</b>"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title_font_size=16,
        xaxis_title="Sales ($)", yaxis_title="",
        coloraxis_showscale=False,
        **DARK_LAYOUT
    )
    return fig

def plot_rfm_clusters(rfm_df: pd.DataFrame) -> go.Figure:
    """Creates a 3D Scatter plot for Recency vs Frequency vs Monetary with Cluster Segment coloring."""
    if rfm_df.empty or "Segment_Name" not in rfm_df.columns:
        return go.Figure()

    fig = px.scatter_3d(
        rfm_df,
        x="Recency", y="Frequency", z="Monetary",
        color="Segment_Name",
        hover_data=["Customer_Name", "RFM_Score"],
        opacity=0.8,
        color_discrete_sequence=COLOR_SEQUENCE,
        title="<b>Customer Segmentation (RFM 3D Clusters)</b>"
    )
    fig.update_traces(marker=dict(size=5, line=dict(width=0.5, color="white")))
    fig.update_layout(
        title_font_size=16,
        scene=dict(
            xaxis_title="Recency (Days)",
            yaxis_title="Frequency (Orders)",
            zaxis_title="Monetary ($)",
            bgcolor="rgba(11, 15, 25, 0.8)"
        ),
        **DARK_LAYOUT
    )
    return fig

def plot_discount_impact(discount_df: pd.DataFrame) -> go.Figure:
    """Bar chart showing Margin % across Discount Brackets."""
    if discount_df.empty:
        return go.Figure()

    fig = px.bar(
        discount_df, x="Discount_Bracket", y="Margin_%",
        color="Margin_%",
        color_continuous_scale="RdYlGn",
        text=discount_df["Margin_%"].apply(lambda v: f"{v:.1f}%"),
        title="<b>Profit Margin % vs Discount Bracket</b>"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title_font_size=16,
        xaxis_title="Discount Bracket", yaxis_title="Profit Margin %",
        coloraxis_showscale=False,
        **DARK_LAYOUT
    )
    return fig

def plot_actual_vs_predicted_forecast(
    df_hist: pd.DataFrame,
    df_test_pred: pd.DataFrame,
    df_future: pd.DataFrame,
    title: str = "LSTM Sales Forecast (Historical vs Test vs Future 30/60/90 Days)"
) -> go.Figure:
    """
    Creates an interactive time-series chart showing:
    1. Historical Actual Sales (Blue)
    2. Model Test Predictions (Green)
    3. Future Forecast Projection (Purple line with confidence band)
    """
    fig = go.Figure()

    # Historical
    if not df_hist.empty:
        fig.add_trace(go.Scatter(
            x=df_hist["Date"], y=df_hist["Sales"],
            name="Historical Sales", mode="lines",
            line=dict(color=COLOR_PRIMARY, width=2.5)
        ))

    # Test Prediction
    if not df_test_pred.empty:
        fig.add_trace(go.Scatter(
            x=df_test_pred["Date"], y=df_test_pred["Predicted_Sales"],
            name="LSTM Test Fit", mode="lines",
            line=dict(color=COLOR_SUCCESS, width=2, dash="dash")
        ))

    # Future Forecast
    if not df_future.empty:
        fig.add_trace(go.Scatter(
            x=df_future["Date"], y=df_future["Forecasted_Sales"],
            name="Future LSTM Forecast", mode="lines+markers",
            line=dict(color=COLOR_SECONDARY, width=3),
            marker=dict(size=5)
        ))

    fig.update_layout(
        title=f"<b>{title}</b>",
        title_font_size=16,
        xaxis_title="Date", yaxis_title="Daily Sales ($)",
        hovermode="x unified",
        **DARK_LAYOUT
    )
    return fig

def plot_training_loss(history_dict: dict) -> go.Figure:
    """Plots Neural Network Training vs Validation Loss across epochs."""
    fig = go.Figure()

    epochs = list(range(1, len(history_dict.get("loss", [])) + 1))
    fig.add_trace(go.Scatter(
        x=epochs, y=history_dict.get("loss", []),
        name="Training Loss (MSE)", mode="lines+markers",
        line=dict(color=COLOR_PRIMARY, width=2.5)
    ))

    if "val_loss" in history_dict:
        fig.add_trace(go.Scatter(
            x=epochs, y=history_dict.get("val_loss", []),
            name="Validation Loss (MSE)", mode="lines+markers",
            line=dict(color=COLOR_WARNING, width=2.5, dash="dot")
        ))

    fig.update_layout(
        title="<b>LSTM Model Training vs Validation Loss Curve</b>",
        title_font_size=16,
        xaxis_title="Epoch", yaxis_title="Loss (Mean Squared Error)",
        **DARK_LAYOUT
    )
    return fig
