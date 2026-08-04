"""
InsightAI – AI-Powered Business Intelligence Platform
Main Application Entry Point & Navigation Controller
"""

import os
import streamlit as st
import pandas as pd

from utils.data_loader import generate_sample_dataset, validate_dataset
from utils.data_cleaner import clean_dataset
from utils.eda import calculate_kpis
from utils.customer_analytics import calculate_rfm, segment_customers_kmeans
from utils.logger import logger
from models.lstm_forecaster import LSTMSalesForecaster

# 1. Global Page Config
st.set_page_config(
    page_title="InsightAI – Business Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Dark SaaS Styling
def load_css(css_path: str = "assets/style.css"):
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 3. Session State Initialization
@st.cache_data
def get_default_dataset() -> pd.DataFrame:
    sample_path = "data/sample_sales_data.csv"
    if os.path.exists(sample_path):
        return pd.read_csv(sample_path)
    return generate_sample_dataset(num_records=1500, save_path=sample_path)

if "df_raw" not in st.session_state:
    st.session_state["df_raw"] = get_default_dataset()

if "df_clean" not in st.session_state:
    clean_df, health = clean_dataset(st.session_state["df_raw"])
    st.session_state["df_clean"] = clean_df
    st.session_state["data_health"] = health

if "kpis" not in st.session_state:
    st.session_state["kpis"] = calculate_kpis(st.session_state["df_clean"])

if "rfm_df" not in st.session_state:
    rfm = calculate_rfm(st.session_state["df_clean"])
    rfm_clustered, summary = segment_customers_kmeans(rfm, n_clusters=4)
    st.session_state["rfm_df"] = rfm_clustered
    st.session_state["kmeans_summary"] = summary

if "forecaster" not in st.session_state:
    st.session_state["forecaster"] = LSTMSalesForecaster()

# 4. Sidebar Branding & Overview
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #60A5FA; margin:0;'>⚡ InsightAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9CA3AF; font-size: 0.85rem;'>Enterprise AI BI Platform</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### 📌 Active Dataset Status")
    df_active = st.session_state.get("df_clean", pd.DataFrame())
    st.markdown(f"**Rows:** `{len(df_active):,}` | **Cols:** `{len(df_active.columns)}`")
    
    val_status, missing_cols = validate_dataset(df_active)
    if val_status:
        st.success("✅ Dataset Validated", icon="✅")
    else:
        st.error(f"⚠️ Missing columns: {missing_cols}")

    st.divider()
    st.caption("🚀 Powered by Streamlit, Scikit-Learn & TensorFlow")

# 5. Welcome Screen / Landing Entry
st.markdown("<h1 class='main-title'>Welcome to InsightAI Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Select a module from the left sidebar navigation to begin analyzing sales data, customer segments, AI insights, and deep learning forecasts.</p>", unsafe_allow_html=True)

# Executive KPI Strip
kpis = st.session_state.get("kpis", {})
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class='metric-card blue'>
        <div class='metric-title'>Total Revenue</div>
        <div class='metric-value'>${kpis.get('total_revenue', 0):,.2f}</div>
        <div class='metric-delta delta-positive'>↑ {kpis.get('rev_growth_mom', 0):.1f}% MoM</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='metric-card emerald'>
        <div class='metric-title'>Total Profit</div>
        <div class='metric-value'>${kpis.get('total_profit', 0):,.2f}</div>
        <div class='metric-delta delta-positive'>Margin: {kpis.get('profit_margin', 0):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='metric-card purple'>
        <div class='metric-title'>Total Orders</div>
        <div class='metric-value'>{kpis.get('total_orders', 0):,}</div>
        <div class='metric-delta delta-neutral'>Volume</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='metric-card amber'>
        <div class='metric-title'>Unique Customers</div>
        <div class='metric-value'>{kpis.get('total_customers', 0):,}</div>
        <div class='metric-delta delta-neutral'>Active Base</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class='metric-card rose'>
        <div class='metric-title'>Avg Order Value</div>
        <div class='metric-value'>${kpis.get('aov', 0):,.2f}</div>
        <div class='metric-delta delta-positive'>Per Basket</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("""
    <div class='glass-card'>
        <h3>🚀 Quick Start Guide</h3>
        <ol style='color: #D1D5DB; line-height: 1.8;'>
            <li><b>1. Home:</b> Review architecture matrix & tech stack.</li>
            <li><b>2. Upload Dataset:</b> Upload custom retail sales CSV/Excel files or use pre-loaded dataset.</li>
            <li><b>3. Data Cleaning:</b> Execute data hygiene, date parsing & duplicate removal.</li>
            <li><b>4. Dashboard:</b> Explore interactive executive BI charts & regional filters.</li>
            <li><b>5. Customer Analytics:</b> Run RFM scoring & Scikit-Learn KMeans clustering.</li>
            <li><b>6. Product Analytics:</b> Analyze profitability, top champions & bottom laggards.</li>
            <li><b>7. AI Business Insights:</b> Review automatically generated business recommendations & risk flags.</li>
            <li><b>8. LSTM Sales Forecasting:</b> Train TensorFlow LSTM deep learning model for 30/60/90-day future forecasts.</li>
            <li><b>9. Reports:</b> Download formatted Multi-Sheet Excel workbooks & executive summaries.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class='glass-card'>
        <h3>💡 Platform Architecture</h3>
        <ul style='color: #D1D5DB; line-height: 1.8;'>
            <li><b>Backend:</b> Python 3.12+</li>
            <li><b>Frontend:</b> Streamlit SaaS UI</li>
            <li><b>ML Engine:</b> Scikit-Learn KMeans</li>
            <li><b>DL Engine:</b> TensorFlow / Keras LSTM</li>
            <li><b>Charts:</b> Plotly Interactive</li>
            <li><b>Export:</b> OpenPyXL & Pandas</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
