"""
InsightAI Page 8: TensorFlow/Keras LSTM Deep Learning Sales Forecasting
"""

import streamlit as st
import pandas as pd
from models.lstm_forecaster import LSTMSalesForecaster
from charts.plotly_charts import plot_actual_vs_predicted_forecast, plot_training_loss

st.set_page_config(page_title="InsightAI - LSTM Forecasting", page_icon="📈", layout="wide")

st.markdown("<h1 class='main-title'>🤖 Deep Learning LSTM Sales Forecasting</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Predict future daily sales demand using TensorFlow/Keras Long Short-Term Memory (LSTM) recurrent neural networks.</p>", unsafe_allow_html=True)

df_clean = st.session_state.get("df_clean", pd.DataFrame())

if df_clean.empty or "Order_Date" not in df_clean.columns:
    st.warning("No time-series date column found in dataset.")
    st.stop()

forecaster: LSTMSalesForecaster = st.session_state.get("forecaster", LSTMSalesForecaster())
daily_series = forecaster.prepare_daily_series(df_clean)

col_ctrl, col_info = st.columns([1, 1])

with col_ctrl:
    st.markdown("### ⚙️ Model Hyperparameters & Controls")
    seq_len = st.slider("Lookback Sequence Window (Days)", min_value=7, max_value=30, value=14)
    epochs_ui = st.slider("Training Epochs", min_value=5, max_value=50, value=20, step=5)
    batch_size_ui = st.select_slider("Batch Size", options=[8, 16, 32, 64], value=16)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🚀 Train LSTM Neural Network", use_container_width=True):
            with st.spinner("Training TensorFlow Keras LSTM neural network..."):
                try:
                    forecaster.sequence_length = seq_len
                    res = forecaster.fit(daily_series, epochs=epochs_ui, batch_size=batch_size_ui)
                    st.session_state["forecaster"] = forecaster
                    st.session_state["lstm_results"] = res
                    forecaster.save()
                    st.success("✅ LSTM Model Trained & Saved to Disk!")
                except Exception as e:
                    st.error(f"Training failed: {str(e)}")

    with col_b2:
        if st.button("📂 Load Saved Model", use_container_width=True):
            if forecaster.load():
                st.session_state["forecaster"] = forecaster
                st.success("Loaded trained LSTM model from disk!")
            else:
                st.warning("No pre-trained model found in saved_models/")

with col_info:
    st.markdown("### 🧠 Neural Network Architecture")
    st.markdown("""
    - **Layer 1:** `Input(seq_len, 1)` -> `LSTM(64, return_sequences=True)`
    - **Dropout:** `Dropout(0.2)`
    - **Layer 2:** `LSTM(32, return_sequences=False)`
    - **Dropout:** `Dropout(0.2)`
    - **Dense:** `Dense(16, activation='relu')` -> `Dense(1)`
    - **Optimizer:** `Adam(lr=0.001)` | **Loss Function:** `MSE`
    """)

st.divider()

# Results Display
lstm_res = st.session_state.get("lstm_results", {})

if lstm_res:
    metrics = lstm_res.get("metrics", {})
    history = lstm_res.get("history", {})
    test_pred_df = lstm_res.get("test_pred_df", pd.DataFrame())

    st.markdown("### 📊 Model Performance Evaluation Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mean Absolute Error (MAE)", f"${metrics.get('mae', 0):,.2f}")
    m2.metric("Root Mean Squared Error (RMSE)", f"${metrics.get('rmse', 0):,.2f}")
    m3.metric("Mean Absolute Percentage Error (MAPE)", f"{metrics.get('mape', 0):.2f}%")
    m4.metric("Test Samples Evaluated", f"{metrics.get('test_samples', 0)}")

    col_loss, col_forecast_opt = st.columns([1, 1])

    with col_loss:
        fig_loss = plot_training_loss(history)
        st.plotly_chart(fig_loss, use_container_width=True)

    with col_forecast_opt:
        st.markdown("### 🔮 Future Demand Forecasting Options")
        days_forecast = st.radio("Select Future Horizon", options=[30, 60, 90], format_func=lambda x: f"Next {x} Days", horizontal=True)
        
        future_df = forecaster.forecast_future(daily_series, days_ahead=days_forecast)
        st.session_state["future_df"] = future_df

        st.dataframe(future_df.head(10), use_container_width=True)

    st.divider()

    st.markdown("### 📈 Interactive Actual vs Predicted vs Future Forecast")
    fig_fc = plot_actual_vs_predicted_forecast(
        df_hist=daily_series.rename(columns={"Order_Date": "Date"}),
        df_test_pred=test_pred_df,
        df_future=st.session_state.get("future_df", pd.DataFrame()),
        title=f"LSTM Daily Sales Forecast - Next {days_forecast} Days Projection"
    )
    st.plotly_chart(fig_fc, use_container_width=True)
else:
    st.info("👈 Click **Train LSTM Neural Network** to begin time-series forecasting training.")
