"""
InsightAI Page 6: Product Profitability Analytics
"""

import streamlit as st
import pandas as pd
from utils.product_analytics import get_product_performance
from charts.plotly_charts import plot_top_products_bar

st.set_page_config(page_title="InsightAI - Product Analytics", page_icon="📦", layout="wide")

st.markdown("<h1 class='main-title'>📦 Product Profitability Analytics</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Evaluate product performance, profit margin contribution, and identify underperforming item laggards.</p>", unsafe_allow_html=True)

df_clean = st.session_state.get("df_clean", pd.DataFrame())

if df_clean.empty or "Product_Name" not in df_clean.columns:
    st.warning("No product data available in dataset.")
    st.stop()

prod_perf = get_product_performance(df_clean, top_n=10)

col1, col2 = st.columns(2)

with col1:
    fig_top = plot_top_products_bar(prod_perf["top_revenue"], title="Top 10 Products by Sales Revenue ($)")
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    fig_prof = plot_top_products_bar(prod_perf["top_profit"], title="Top 10 Products by Net Profit ($)")
    st.plotly_chart(fig_prof, use_container_width=True)

st.divider()

st.markdown("### 🛑 Underperforming Product Laggards (Lowest Net Profit)")
st.dataframe(
    prod_perf["bottom_profit"][["Product_Name", "Category", "Sub_Category", "Total_Sales", "Total_Profit", "Profit_Margin_%"]],
    use_container_width=True
)

st.divider()

st.markdown("### 🏷️ Category Performance Overview")
st.dataframe(prod_perf["category_summary"], use_container_width=True)
