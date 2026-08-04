"""
InsightAI Page 1: Home & Executive Product Overview
"""

import streamlit as st

st.set_page_config(page_title="InsightAI - Home", page_icon="🏠", layout="wide")

st.markdown("<h1 class='main-title'>InsightAI – AI-Powered Business Intelligence Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Production-grade SaaS analytical platform for retail sales analytics, customer segmentation, automated AI recommendations, and deep learning forecasting.</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='glass-card'>
        <h3 style='color: #60A5FA;'>📊 Executive Dashboard</h3>
        <p style='color: #D1D5DB;'>Real-time KPI metrics, monthly/quarterly sales trends, profit margins, regional performance, and interactive Plotly visualizers.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='glass-card'>
        <h3 style='color: #A78BFA;'>👥 Customer ML Segmentation</h3>
        <p style='color: #D1D5DB;'>Recency, Frequency, Monetary (RFM) behavioral scoring paired with Scikit-Learn KMeans clustering & Silhouette evaluation.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='glass-card'>
        <h3 style='color: #34D399;'>🤖 Deep Learning Forecasting</h3>
        <p style='color: #D1D5DB;'>TensorFlow/Keras LSTM neural network time-series engine for predicting future 30, 60, and 90-day sales demand.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("## 🛠️ Enterprise Architecture & Technology Stack")

tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)

with tech_col1:
    st.markdown("""
    **Core & Data Stack**
    - `Python 3.12+`
    - `Pandas 2.1+`
    - `NumPy 1.26+`
    - `OpenPyXL 3.1+`
    """)

with tech_col2:
    st.markdown("""
    **Machine Learning & AI**
    - `Scikit-Learn` (KMeans & Scaling)
    - `TensorFlow 2.15+` (Keras LSTM)
    - `Joblib` (Model Serialization)
    """)

with tech_col3:
    st.markdown("""
    **UI & Visualization**
    - `Streamlit 1.35+`
    - `Plotly Express & GraphObjects`
    - `Custom SaaS Dark CSS`
    """)

with tech_col4:
    st.markdown("""
    **DevOps & Packaging**
    - `Docker & Docker Compose`
    - `PEP8 Compliant Codebase`
    - `Streamlit Cloud Ready`
    """)

st.divider()

st.markdown("## 🎯 Business Value Proposition")

st.markdown("""
1. **Automated Insights**: Replaces manual spreadsheet analysis with instant rule-based AI recommendations highlighting revenue drivers and loss-making discounts.
2. **Predictive Inventory**: Uses deep learning time-series models (LSTM) to forecast demand peaks 90 days out, reducing inventory stockout and overstock carrying costs.
3. **Targeted Customer Retention**: Identifies high-value "Champions" vs "At-Risk" customer cohorts using 3D RFM KMeans clustering for tailored marketing campaigns.
4. **Export Ready**: Generates executive presentation-ready multi-sheet Excel reports with automated styling and formatting.
""")
