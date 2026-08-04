"""
InsightAI Page 4: Executive BI Dashboard
"""

import streamlit as st
import pandas as pd
from utils.eda import calculate_kpis, get_monthly_trends
from utils.product_analytics import get_product_performance, get_discount_impact
from charts.plotly_charts import (
    plot_monthly_sales_trend,
    plot_category_distribution,
    plot_regional_performance,
    plot_top_products_bar,
    plot_discount_impact
)

st.set_page_config(page_title="InsightAI - Dashboard", page_icon="📊", layout="wide")

st.markdown("<h1 class='main-title'>📊 Executive BI Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Interactive business intelligence overview with real-time dynamic filters and multi-tab drill-down visualizers.</p>", unsafe_allow_html=True)

df_clean = st.session_state.get("df_clean", pd.DataFrame())

if df_clean.empty:
    st.warning("No dataset loaded. Please upload or load data.")
    st.stop()

# Filter Controls Bar
with st.expander("🎛️ Interactive Dashboard Filters", expanded=True):
    col_f1, col_f2, col_f3 = st.columns(3)

    min_date = pd.to_datetime(df_clean["Order_Date"]).min().date() if "Order_Date" in df_clean.columns else None
    max_date = pd.to_datetime(df_clean["Order_Date"]).max().date() if "Order_Date" in df_clean.columns else None

    with col_f1:
        if min_date and max_date:
            date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        else:
            date_range = None

    with col_f2:
        all_regions = sorted(df_clean["Region"].dropna().unique()) if "Region" in df_clean.columns else []
        selected_regions = st.multiselect("Region", options=all_regions, default=all_regions)

    with col_f3:
        all_categories = sorted(df_clean["Category"].dropna().unique()) if "Category" in df_clean.columns else []
        selected_categories = st.multiselect("Category", options=all_categories, default=all_categories)

# Apply Filter Logic
df_filtered = df_clean.copy()

if date_range and len(date_range) == 2:
    start_d, end_d = date_range
    df_filtered["Order_Date"] = pd.to_datetime(df_filtered["Order_Date"])
    df_filtered = df_filtered[(df_filtered["Order_Date"].dt.date >= start_d) & (df_filtered["Order_Date"].dt.date <= end_d)]

if selected_regions and "Region" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]

if selected_categories and "Category" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

# Calculate Filtered KPIs
kpis = calculate_kpis(df_filtered)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", f"${kpis['total_revenue']:,.2f}", f"{kpis['rev_growth_mom']:.1f}% MoM")
c2.metric("Profit", f"${kpis['total_profit']:,.2f}", f"Margin: {kpis['profit_margin']:.1f}%")
c3.metric("Orders", f"{kpis['total_orders']:,}")
c4.metric("Customers", f"{kpis['total_customers']:,}")
c5.metric("Avg Order Value", f"${kpis['aov']:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Dashboard Multi-Tab View
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Sales & Profit Trends",
    "🗺️ Regional & Category Matrix",
    "🏆 Top Products & Champions",
    "📉 Discount & Margin Elasticity"
])

with tab1:
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        monthly_df = get_monthly_trends(df_filtered)
        fig_trend = plot_monthly_sales_trend(monthly_df)
        st.plotly_chart(fig_trend, use_container_width=True)
    with col_t2:
        fig_cat = plot_category_distribution(df_filtered)
        st.plotly_chart(fig_cat, use_container_width=True)

with tab2:
    col_r1, col_r2 = st.columns([1, 1])
    with col_r1:
        fig_reg = plot_regional_performance(df_filtered)
        st.plotly_chart(fig_reg, use_container_width=True)
    with col_r2:
        st.markdown("### 📦 Sub-Category Sales & Profit Breakdown")
        if "Sub_Category" in df_filtered.columns:
            sub_df = df_filtered.groupby(["Category", "Sub_Category"]).agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Orders=("Order_ID", "nunique")
            ).reset_index().sort_values(by="Sales", ascending=False)
            st.dataframe(sub_df, use_container_width=True, height=380)

with tab3:
    prod_perf = get_product_performance(df_filtered, top_n=10)
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        fig_top_prod = plot_top_products_bar(prod_perf["top_revenue"], title="Top 10 Products by Sales Revenue")
        st.plotly_chart(fig_top_prod, use_container_width=True)
    with col_p2:
        st.markdown("### ⚠️ Bottom 10 Products by Net Profit")
        st.dataframe(prod_perf["bottom_profit"][["Product_Name", "Category", "Total_Sales", "Total_Profit", "Profit_Margin_%"]], use_container_width=True)

with tab4:
    disc_df = get_discount_impact(df_filtered)
    col_d1, col_d2 = st.columns([3, 2])
    with col_d1:
        fig_disc = plot_discount_impact(disc_df)
        st.plotly_chart(fig_disc, use_container_width=True)
    with col_d2:
        st.markdown("### 💡 Discount Elasticity Table")
        st.dataframe(disc_df, use_container_width=True)
