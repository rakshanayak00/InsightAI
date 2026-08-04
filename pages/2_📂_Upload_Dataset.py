"""
InsightAI Page 2: Upload Dataset & Validation
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, validate_dataset, generate_sample_dataset
from utils.eda import calculate_kpis
from utils.data_cleaner import clean_dataset
from utils.customer_analytics import calculate_rfm, segment_customers_kmeans

st.set_page_config(page_title="InsightAI - Upload Dataset", page_icon="📂", layout="wide")

st.markdown("<h1 class='main-title'>📂 Dataset Management & Validation</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Upload custom sales datasets or reload the pre-packaged synthetic retail sales dataset.</p>", unsafe_allow_html=True)

col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])

with col_sample:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reload Sample Dataset", use_container_width=True):
        sample_df = generate_sample_dataset(num_records=1500, save_path="data/sample_sales_data.csv")
        st.session_state["df_raw"] = sample_df
        clean_df, health = clean_dataset(sample_df)
        st.session_state["df_clean"] = clean_df
        st.session_state["data_health"] = health
        st.session_state["kpis"] = calculate_kpis(clean_df)
        rfm = calculate_rfm(clean_df)
        rfm_c, summary = segment_customers_kmeans(rfm)
        st.session_state["rfm_df"] = rfm_c
        st.session_state["kmeans_summary"] = summary
        st.success("Sample dataset reloaded successfully!")

if uploaded_file is not None:
    try:
        df_uploaded = load_data(uploaded_file)
        st.session_state["df_raw"] = df_uploaded
        clean_df, health = clean_dataset(df_uploaded)
        st.session_state["df_clean"] = clean_df
        st.session_state["data_health"] = health
        st.session_state["kpis"] = calculate_kpis(clean_df)
        rfm = calculate_rfm(clean_df)
        rfm_c, summary = segment_customers_kmeans(rfm)
        st.session_state["rfm_df"] = rfm_c
        st.session_state["kmeans_summary"] = summary
        st.success(f"Successfully loaded '{uploaded_file.name}' with {len(df_uploaded):,} rows!")
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")

df_current = st.session_state.get("df_raw", pd.DataFrame())

if not df_current.empty:
    st.divider()
    st.markdown("### 🔍 Dataset Schema & Column Validation")

    is_valid, missing_cols = validate_dataset(df_current)

    if is_valid:
        st.success("✅ **Dataset Schema Validated!** All required columns (`Order_ID`, `Order_Date`, `Sales`, `Profit`, `Customer_ID`, `Category`, `Region`) are present.")
    else:
        st.warning(f"⚠️ **Missing Schema Columns:** {missing_cols}. Some dashboard features may require these column names.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", f"{len(df_current):,}")
    m2.metric("Total Columns", f"{len(df_current.columns)}")
    m3.metric("Duplicate Rows", f"{df_current.duplicated().sum():,}")
    m4.metric("Total Null Values", f"{df_current.isnull().sum().sum():,}")

    st.markdown("### 📋 Dataset Preview (First 50 Rows)")
    st.dataframe(df_current.head(50), use_container_width=True)

    st.markdown("### 📊 Column Data Types & Non-Null Counts")
    dtype_df = pd.DataFrame({
        "Column": df_current.columns,
        "Data Type": [str(t) for t in df_current.dtypes],
        "Non-Null Count": df_current.notnull().sum().values,
        "Null Count": df_current.isnull().sum().values
    })
    st.dataframe(dtype_df, use_container_width=True)
