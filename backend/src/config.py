from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

RAW_DETAIL_PATH = RAW_DIR / "infractions_detail.csv"
RAW_SUBTOTALS_PATH = RAW_DIR / "infractions_sous_totaux.csv"
RAW_TOTALS_PATH = RAW_DIR / "infractions_totaux_generaux.csv"

CLEAN_DATA_PATH = PROCESSED_DIR / "infractions_clean.csv"
CLUSTERED_DATA_PATH = PROCESSED_DIR / "infractions_clustered.csv"
ANOMALIES_DATA_PATH = PROCESSED_DIR / "infractions_anomalies.csv"
ENRICHED_DATA_PATH = PROCESSED_DIR / "infractions_enriched.csv"
RECONCILIATION_PATH = PROCESSED_DIR / "reconciliation_totaux.csv"
QUALITY_REPORT_PATH = PROCESSED_DIR / "data_quality_report.json"

REGRESSION_MODEL_PATH = ARTIFACTS_DIR / "best_regression_model.joblib"
REGRESSION_METRICS_PATH = ARTIFACTS_DIR / "regression_metrics.json"
REGRESSION_PREDICTIONS_PATH = ARTIFACTS_DIR / "regression_predictions.csv"
CLUSTER_MODEL_PATH = ARTIFACTS_DIR / "kmeans_model.joblib"
CLUSTER_METRICS_PATH = ARTIFACTS_DIR / "clustering_metrics.json"
ANOMALY_MODEL_PATH = ARTIFACTS_DIR / "isolation_forest_model.joblib"
ANOMALY_METRICS_PATH = ARTIFACTS_DIR / "anomaly_metrics.json"

_default_db = f"sqlite:///{(DATA_DIR / 'criminalite.db').as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", _default_db)
# Render et certains fournisseurs exposent une URL PostgreSQL sans préciser le
# pilote. Le projet utilise psycopg 3, donc on normalise automatiquement l'URL.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
