"""
InsightAI Page 7: AI Business Recommendation Engine
"""

import streamlit as st
import pandas as pd
from utils.ai_insights import generate_ai_insights

st.set_page_config(page_title="InsightAI - AI Business Insights", page_icon="💡", layout="wide")

st.markdown("<h1 class='main-title'>💡 Automated AI Business Insights</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Heuristic business intelligence engine analyzing sales patterns, margin risks, regional drivers, and discounting impact.</p>", unsafe_allow_html=True)

df_clean = st.session_state.get("df_clean", pd.DataFrame())

if df_clean.empty:
    st.warning("No dataset loaded. Please upload or load data.")
    st.stop()

insights = generate_ai_insights(df_clean)

if not insights:
    st.info("No active insight anomalies detected for the current dataset parameters.")
    st.stop()

st.markdown(f"### 🎯 Active Executive Strategic Recommendations ({len(insights)} Insights Found)")

# Render Custom Insight Cards
for ins in insights:
    card_type = ins["type"]
    tag_class = f"tag-{card_type}"
    card_class = f"insight-card {card_type}"

    st.markdown(f"""
    <div class='{card_class}'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <span class='insight-tag {tag_class}'>{ins['type'].upper()} • {ins['category']}</span>
            <span style='color: #60A5FA; font-weight: 700; font-size: 0.9rem;'>{ins['metric']}</span>
        </div>
        <h4 style='color: #F9FAFB; margin: 6px 0 10px 0;'>{ins['title']}</h4>
        <p style='color: #D1D5DB; margin-bottom: 8px;'><b>Insight:</b> {ins['message']}</p>
        <p style='color: #34D399; margin-bottom: 0;'><b>💡 Recommended Action:</b> {ins['recommendation']}</p>
    </div>
    """, unsafe_allow_html=True)
