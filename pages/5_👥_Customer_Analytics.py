"""
InsightAI Page 5: Customer Analytics & Scikit-Learn KMeans Clustering
"""

import streamlit as st
import pandas as pd
from utils.customer_analytics import calculate_rfm, segment_customers_kmeans
from charts.plotly_charts import plot_rfm_clusters

st.set_page_config(page_title="InsightAI - Customer Analytics", page_icon="👥", layout="wide")

st.markdown("<h1 class='main-title'>👥 Customer Behavioral Segmentation</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>RFM (Recency, Frequency, Monetary) behavioral profiling powered by Scikit-Learn KMeans unsupervised clustering.</p>", unsafe_allow_html=True)

df_clean = st.session_state.get("df_clean", pd.DataFrame())

if df_clean.empty or "Customer_ID" not in df_clean.columns:
    st.warning("No dataset or Customer_ID column available.")
    st.stop()

rfm_base = calculate_rfm(df_clean)

st.markdown("### ⚙️ KMeans Clustering Tuning Controls")

col_tune, col_metrics = st.columns([1, 1])

with col_tune:
    n_clusters_ui = st.slider("Select Number of Customer Clusters (k)", min_value=2, max_value=8, value=4, step=1)
    
    rfm_clustered, km_summary = segment_customers_kmeans(rfm_base, n_clusters=n_clusters_ui)
    st.session_state["rfm_df"] = rfm_clustered
    st.session_state["kmeans_summary"] = km_summary

with col_metrics:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Total Customers Evaluated", f"{len(rfm_clustered):,}")
    c2.metric("KMeans Silhouette Score", f"{km_summary['silhouette_score']:.3f}", "Cluster Quality (>0.3 Good)")

st.divider()

# Visualization Section
col_vis1, col_vis2 = st.columns([3, 2])

with col_vis1:
    fig_3d = plot_rfm_clusters(rfm_clustered)
    st.plotly_chart(fig_3d, use_container_width=True)

with col_vis2:
    st.markdown("### 📊 Segment Distribution Summary")
    seg_summary = rfm_clustered.groupby("Segment_Name").agg(
        Customer_Count=("Customer_ID", "count"),
        Avg_Recency_Days=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Spend_Monetary=("Monetary", "mean")
    ).reset_index().sort_values(by="Avg_Spend_Monetary", ascending=False)

    st.dataframe(seg_summary, use_container_width=True)

st.divider()

st.markdown("### 📋 Individual Customer RFM Scoring Table")
st.dataframe(
    rfm_clustered[["Customer_ID", "Customer_Name", "Segment_Name", "Recency", "Frequency", "Monetary", "RFM_Score", "RFM_Cell"]],
    use_container_width=True,
    height=400
)
