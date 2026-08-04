"""
Customer Analytics Utility Module for InsightAI.
Implements Recency, Frequency, Monetary (RFM) analysis and Scikit-Learn KMeans Clustering.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from utils.logger import logger

def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Recency, Frequency, and Monetary (RFM) metrics for each customer.
    """
    if df.empty or "Customer_ID" not in df.columns or "Order_Date" not in df.columns:
        return pd.DataFrame()

    df_temp = df.copy()
    df_temp["Order_Date"] = pd.to_datetime(df_temp["Order_Date"])
    max_date = df_temp["Order_Date"].max() + pd.Timedelta(days=1)

    rfm = df_temp.groupby("Customer_ID").agg(
        Recency=("Order_Date", lambda date: (max_date - date.max()).days),
        Frequency=("Order_ID", "nunique"),
        Monetary=("Sales", "sum"),
        Customer_Name=("Customer_Name", "first"),
        Segment=("Segment", "first")
    ).reset_index()

    # Calculate RFM Scores (1 to 4 quantiles)
    rfm["R_Score"] = pd.qcut(rfm["Recency"], q=4, labels=[4, 3, 2, 1], duplicates="drop").astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=4, labels=[1, 2, 3, 4], duplicates="drop").astype(int)

    rfm["RFM_Cell"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    return rfm

def segment_customers_kmeans(rfm_df: pd.DataFrame, n_clusters: int = 4) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Performs KMeans customer segmentation on scaled RFM features.
    Returns (clustered_rfm_df, cluster_summary_dict).
    """
    if rfm_df.empty or len(rfm_df) < n_clusters:
        return rfm_df, {"silhouette_score": 0.0, "cluster_means": pd.DataFrame()}

    features = ["Recency", "Frequency", "Monetary"]
    X = rfm_df[features].copy()

    # Log transform monetary & recency to handle skewness
    X["Recency"] = np.log1p(X["Recency"])
    X["Frequency"] = np.log1p(X["Frequency"])
    X["Monetary"] = np.log1p(X["Monetary"])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm_df["Cluster"] = kmeans.fit_predict(X_scaled)

    # Compute Silhouette Score
    score = float(silhouette_score(X_scaled, rfm_df["Cluster"])) if len(rfm_df) > n_clusters else 0.0

    # Assign meaningful cluster segment names based on average monetary & recency
    cluster_means = rfm_df.groupby("Cluster").agg({
        "Recency": "mean",
        "Frequency": "mean",
        "Monetary": "mean",
        "Customer_ID": "count"
    }).reset_index()

    # Sort clusters by Monetary value descending
    cluster_means = cluster_means.sort_values(by="Monetary", ascending=False)
    
    segment_names = ["Champions (High Value)", "Loyal Customers", "Potential Loyalists", "At Risk / Inactive"]
    name_mapping = {}
    for i, cluster_id in enumerate(cluster_means["Cluster"]):
        name_mapping[cluster_id] = segment_names[i] if i < len(segment_names) else f"Segment {i+1}"

    rfm_df["Segment_Name"] = rfm_df["Cluster"].map(name_mapping)

    summary = {
        "silhouette_score": round(score, 3),
        "cluster_means": cluster_means,
        "n_clusters": n_clusters
    }

    logger.info(f"KMeans segmentation executed with k={n_clusters}. Silhouette Score: {summary['silhouette_score']}")

    return rfm_df, summary
