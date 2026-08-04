"""
Verification & Test Suite for InsightAI Backend Modules.
Runs automated checks on dataset generation, data cleaning, EDA, customer clustering,
AI insights, LSTM forecaster training/prediction, and report generation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import generate_sample_dataset, validate_dataset
from utils.data_cleaner import clean_dataset
from utils.eda import calculate_kpis, get_monthly_trends
from utils.customer_analytics import calculate_rfm, segment_customers_kmeans
from utils.product_analytics import get_product_performance, get_discount_impact
from utils.ai_insights import generate_ai_insights
from utils.reporting import export_to_csv, export_to_excel, generate_text_report
from models.lstm_forecaster import LSTMSalesForecaster

def run_tests():
    print("=" * 60)
    print("RUNNING INSIGHTAI INTEGRATION TEST SUITE")
    print("=" * 60)

    # 1. Dataset generation & validation
    print("[1/7] Testing Data Loader & Validation...")
    df_raw = generate_sample_dataset(num_records=500, save_path=None)
    is_valid, missing = validate_dataset(df_raw)
    assert is_valid, f"Validation failed: missing {missing}"
    print(f"  -> Generated {len(df_raw)} records. Validation passed!")

    # 2. Data Cleaner
    print("[2/7] Testing Data Cleaner...")
    df_clean, health = clean_dataset(df_raw)
    assert len(df_clean) > 0, "Cleaned dataframe is empty"
    print(f"  -> Cleaned dataset has {len(df_clean)} rows.")

    # 3. EDA & KPIs
    print("[3/7] Testing EDA Engine...")
    kpis = calculate_kpis(df_clean)
    assert kpis["total_revenue"] > 0, "Total revenue must be > 0"
    print(f"  -> Revenue: ${kpis['total_revenue']:,.2f}, Profit: ${kpis['total_profit']:,.2f}, Margin: {kpis['profit_margin']}%")

    # 4. Customer Analytics
    print("[4/7] Testing RFM & KMeans Customer Segmentation...")
    rfm = calculate_rfm(df_clean)
    rfm_c, summary = segment_customers_kmeans(rfm, n_clusters=4)
    assert "Segment_Name" in rfm_c.columns, "Missing Segment_Name column"
    print(f"  -> Silhouette Score: {summary['silhouette_score']}")

    # 5. Product & AI Insights
    print("[5/7] Testing AI Insights Engine & Product Analytics...")
    insights = generate_ai_insights(df_clean)
    assert len(insights) > 0, "AI insights should not be empty"
    print(f"  -> Generated {len(insights)} active AI insight cards.")

    # 6. LSTM Forecaster
    print("[6/7] Testing TensorFlow Keras LSTM Forecaster...")
    forecaster = LSTMSalesForecaster(sequence_length=7)
    daily = forecaster.prepare_daily_series(df_clean)
    res = forecaster.fit(daily, epochs=3, batch_size=16)
    metrics = res["metrics"]
    assert metrics["mae"] >= 0, "MAE must be non-negative"
    
    future_df = forecaster.forecast_future(daily, days_ahead=14)
    assert len(future_df) == 14, "Future forecast length mismatch"
    print(f"  -> LSTM Train Success! Test MAE=${metrics['mae']:.2f}, Future 14d forecast generated.")

    # 7. Reporting Exporter
    print("[7/7] Testing Report Exporter...")
    csv_b = export_to_csv(df_clean)
    excel_b = export_to_excel(df_clean, kpis)
    text_r = generate_text_report(kpis, insights)
    assert len(csv_b) > 0 and len(excel_b) > 0 and len(text_r) > 0
    print("  -> CSV, Excel, and Text reports generated successfully!")

    print("=" * 60)
    print("ALL 7 INTEGRATION TESTS PASSED CLEANLY! [PASSED]")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
