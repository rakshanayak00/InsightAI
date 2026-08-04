"""
InsightAI Page 3: Data Cleaning & Hygiene Controls
"""

import streamlit as st
import pandas as pd
from utils.data_cleaner import clean_dataset, get_data_health_summary
from utils.eda import calculate_kpis
from utils.customer_analytics import calculate_rfm, segment_customers_kmeans

st.set_page_config(page_title="InsightAI - Data Cleaning", page_icon="🧹", layout="wide")

st.markdown("<h1 class='main-title'>🧹 Data Cleaning Pipeline</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Inspect data health quality, impute missing values, drop duplicates, and convert data types.</p>", unsafe_allow_html=True)

df_raw = st.session_state.get("df_raw", pd.DataFrame())

if df_raw.empty:
    st.warning("No dataset found. Please upload or load a dataset first.")
    st.stop()

raw_health = get_data_health_summary(df_raw)

col_ctrl, col_stats = st.columns([1, 1])

with col_ctrl:
    st.markdown("### ⚙️ Cleaning Configuration")
    
    null_strategy_ui = st.selectbox(
        "Missing Value Strategy",
        ["impute", "drop", "zero"],
        format_func=lambda x: {
            "impute": "Impute Numeric Nulls with Median",
            "drop": "Drop Rows with Missing Values",
            "zero": "Fill Missing Values with 0"
        }[x]
    )

    drop_dups = st.checkbox("Drop Duplicate Rows", value=True)
    
    if st.button("🧼 Run Cleaning Pipeline", use_container_width=True):
        clean_df, new_health = clean_dataset(
            df_raw,
            null_strategy=null_strategy_ui,
            drop_duplicates=drop_dups
        )
        st.session_state["df_clean"] = clean_df
        st.session_state["data_health"] = new_health
        st.session_state["kpis"] = calculate_kpis(clean_df)
        
        rfm = calculate_rfm(clean_df)
        rfm_c, summary = segment_customers_kmeans(rfm)
        st.session_state["rfm_df"] = rfm_c
        st.session_state["kmeans_summary"] = summary
        
        st.success("✅ Dataset successfully cleaned and updated across all modules!")

with col_stats:
    st.markdown("### 🏥 Data Quality Health Comparison")
    
    current_health = st.session_state.get("data_health", raw_health)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Original Dataset**")
        st.write(f"- Rows: `{raw_health['total_rows']:,}`")
        st.write(f"- Null Values: `{raw_health['total_nulls']:,}`")
        st.write(f"- Duplicate Rows: `{raw_health['duplicate_rows']:,}`")
        st.write(f"- Memory: `{raw_health['memory_mb']} MB`")

    with c2:
        st.markdown("**Cleaned Dataset**")
        st.write(f"- Rows: `{current_health['total_rows']:,}`")
        st.write(f"- Null Values: `{current_health['total_nulls']:,}`")
        st.write(f"- Duplicate Rows: `{current_health['duplicate_rows']:,}`")
        st.write(f"- Memory: `{current_health['memory_mb']} MB`")

st.divider()

st.markdown("### 📋 Cleaned Dataset Inspection")
df_clean = st.session_state.get("df_clean", pd.DataFrame())
st.dataframe(df_clean.head(100), use_container_width=True)
