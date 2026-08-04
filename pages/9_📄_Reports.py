"""
InsightAI Page 9: Executive Reports & Data Exporter
"""

import streamlit as st
import pandas as pd
from utils.reporting import export_to_csv, export_to_excel, generate_text_report
from utils.ai_insights import generate_ai_insights
from utils.product_analytics import get_product_performance

st.set_page_config(page_title="InsightAI - Reports & Exports", page_icon="📄", layout="wide")

st.markdown("<h1 class='main-title'>📄 Reports & Executive Data Exporter</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Export presentation-ready business intelligence reports in Excel, CSV, and Markdown formats.</p>", unsafe_allow_html=True)

df_clean = st.session_state.get("df_clean", pd.DataFrame())
kpis = st.session_state.get("kpis", {})
rfm_df = st.session_state.get("rfm_df", pd.DataFrame())

if df_clean.empty:
    st.warning("No dataset loaded. Please upload or load data.")
    st.stop()

prod_perf = get_product_performance(df_clean)
category_df = prod_perf.get("category_summary", pd.DataFrame())
insights = generate_ai_insights(df_clean)

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    st.markdown("""
    <div class='glass-card'>
        <h3>📊 Multi-Sheet Excel Workbook</h3>
        <p style='color: #9CA3AF;'>Includes styled Executive Summary, Sales Dataset, Category Performance, and Customer RFM Clusters.</p>
    </div>
    """, unsafe_allow_html=True)
    excel_bytes = export_to_excel(df_clean, kpis, category_df, rfm_df)
    st.download_button(
        label="📥 Download Excel Workbook (.xlsx)",
        data=excel_bytes,
        file_name="InsightAI_Executive_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_exp2:
    st.markdown("""
    <div class='glass-card'>
        <h3>📋 Cleaned Sales Dataset CSV</h3>
        <p style='color: #9CA3AF;'>Download the fully preprocessed, cleaned, and typecast raw retail sales data.</p>
    </div>
    """, unsafe_allow_html=True)
    csv_bytes = export_to_csv(df_clean)
    st.download_button(
        label="📥 Download Cleaned Dataset (.csv)",
        data=csv_bytes,
        file_name="InsightAI_Cleaned_Sales_Data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp3:
    st.markdown("""
    <div class='glass-card'>
        <h3>📝 Executive Text Summary</h3>
        <p style='color: #9CA3AF;'>Download concise Markdown report with KPIs and strategic AI business recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    text_report = generate_text_report(kpis, insights)
    st.download_button(
        label="📥 Download Executive Summary (.md)",
        data=text_report,
        file_name="InsightAI_Executive_Summary.md",
        mime="text/markdown",
        use_container_width=True
    )

st.divider()

st.markdown("### 📜 Live Executive Report Preview")
st.markdown(text_report)
