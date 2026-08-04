"""
LSTM Time-Series Sales Forecaster Module for InsightAI.
Implements data aggregation, MinMaxScaler sequence generation, Keras LSTM model compilation,
training, evaluation metrics (MAE, RMSE, MAPE), 30/60/90 day forecasting, and serialization.
"""

import os
from typing import Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import joblib

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

from utils.logger import logger

class LSTMSalesForecaster:
    """
    Production Keras LSTM Sales Forecaster for Retail Time-Series Data.
    """
    def __init__(self, sequence_length: int = 14):
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model: Optional[Sequential] = None
        self.history: Dict[str, list] = {}
        self.is_trained: bool = False

    def prepare_daily_series(self, df: pd.DataFrame, date_col: str = "Order_Date", target_col: str = "Sales") -> pd.DataFrame:
        """Aggregates sales data to a continuous daily time-series."""
        if df.empty or date_col not in df.columns or target_col not in df.columns:
            return pd.DataFrame()

        df_temp = df.copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col])
        daily = df_temp.groupby(date_col)[target_col].sum().reset_index()
        daily = daily.sort_values(by=date_col)

        # Fill missing calendar dates with 0 sales
        daily = daily.set_index(date_col).resample("D").sum().reset_index()
        return daily

    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generates sliding window X (samples, seq_len, 1) and y sequences."""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i : i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)

    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Compiles Keras Sequential LSTM Neural Network."""
        model = Sequential([
            Input(shape=input_shape),
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation="relu"),
            Dense(1)
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="mean_squared_error",
            metrics=["mae"]
        )
        return model

    def fit(self, daily_df: pd.DataFrame, epochs: int = 25, batch_size: int = 16, train_split: float = 0.8) -> Dict[str, Any]:
        """
        Fits the LSTM model on daily sales time series.
        Calculates train/test split, fits scaler, trains model, and logs metrics.
        """
        logger.info(f"Initiating LSTM model training sequence (epochs={epochs}, batch_size={batch_size})...")
        
        sales_values = daily_df["Sales"].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(sales_values)

        X, y = self.create_sequences(scaled_data)
        if len(X) < 10:
            raise ValueError("Insufficient time series data to train LSTM (at least 25 daily observations required).")

        split_idx = int(len(X) * train_split)
        X_train, y_train = X[:split_idx], y[:split_idx]
        X_test, y_test = X[split_idx:], y[split_idx:]

        self.model = self.build_model(input_shape=(self.sequence_length, 1))

        early_stop = EarlyStopping(monitor="val_loss", patience=7, restore_best_weights=True)

        history_obj = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stop],
            verbose=0
        )

        self.history = history_obj.history
        self.is_trained = True

        # Test evaluation
        y_test_pred_scaled = self.model.predict(X_test, verbose=0)
        y_test_actual = self.scaler.inverse_transform(y_test)
        y_test_pred = self.scaler.inverse_transform(y_test_pred_scaled)

        mae = float(mean_absolute_error(y_test_actual, y_test_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test_actual, y_test_pred)))
        
        nonzero_mask = (y_test_actual.flatten() > 0)
        if np.any(nonzero_mask):
            mape = float(np.mean(np.abs((y_test_actual.flatten()[nonzero_mask] - y_test_pred.flatten()[nonzero_mask]) / y_test_actual.flatten()[nonzero_mask])) * 100.0)
        else:
            mape = 0.0

        metrics = {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }

        # Build test dataframe for plotting
        test_dates = daily_df["Order_Date"].iloc[self.sequence_length + split_idx : ].reset_index(drop=True)
        test_pred_df = pd.DataFrame({
            "Date": test_dates[:len(y_test_pred)],
            "Actual_Sales": y_test_actual.flatten(),
            "Predicted_Sales": y_test_pred.flatten()
        })

        logger.info(f"LSTM Training Complete. Metrics: MAE=${mae:.2f}, RMSE=${rmse:.2f}, MAPE={mape:.2f}%")
        return {"metrics": metrics, "test_pred_df": test_pred_df, "history": self.history}

    def forecast_future(self, daily_df: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
        """
        Generates multi-step autoregressive future sales forecast for specified days (e.g. 30, 60, 90).
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before calling forecast_future().")

        sales_values = daily_df["Sales"].values.reshape(-1, 1)
        scaled_data = self.scaler.transform(sales_values)

        # Last sequence window
        current_seq = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)

        future_predictions_scaled = []
        for _ in range(days_ahead):
            next_pred = self.model.predict(current_seq, verbose=0)[0, 0]
            future_predictions_scaled.append(next_pred)

            # Update sliding window sequence
            current_seq = np.append(current_seq[:, 1:, :], [[[next_pred]]], axis=1)

        future_predictions = self.scaler.inverse_transform(np.array(future_predictions_scaled).reshape(-1, 1)).flatten()
        # Enforce non-negative sales
        future_predictions = np.maximum(future_predictions, 0.0)

        last_date = pd.to_datetime(daily_df["Order_Date"].max())
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days_ahead + 1)]

        return pd.DataFrame({
            "Date": future_dates,
            "Forecasted_Sales": np.round(future_predictions, 2)
        })

    def save(self, model_dir: str = "saved_models") -> Tuple[str, str]:
        """Serializes Keras model and MinMaxScaler to disk."""
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "lstm_model.keras")
        scaler_path = os.path.join(model_dir, "scaler.joblib")

        if self.model:
            self.model.save(model_path)
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"LSTM model successfully saved to {model_path}")
            return model_path, scaler_path
        raise ValueError("No trained model to save.")

    def load(self, model_dir: str = "saved_models") -> bool:
        """Loads serialized Keras model and MinMaxScaler from disk."""
        model_path = os.path.join(model_dir, "lstm_model.keras")
        scaler_path = os.path.join(model_dir, "scaler.joblib")

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            self.is_trained = True
            logger.info(f"Loaded LSTM model from {model_path}")
            return True
        return False
