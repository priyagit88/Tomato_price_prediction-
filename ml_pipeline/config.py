"""
Configuration module for the Tomato Price Prediction pipeline.

All sensitive values are read from environment variables with sensible defaults
for local development.
"""

import os
import logging

logger = logging.getLogger(__name__)

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.environ.get(
    "TOMATO_BASE_DIR",
    r"d:\All_projects\tomato_price_prediction",
)
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
PREDICTIONS_DIR = os.path.join(BASE_DIR, "data", "predictions")
MODELS_DIR = os.path.join(BASE_DIR, "models")
ML_PIPELINE_DIR = os.path.join(BASE_DIR, "ml_pipeline")

# ─── Azure SQL Database ─────────────────────────────────────────────────────
DB_CONNECTION_STRING = os.environ.get(
    "TOMATO_DB_CONNECTION_STRING",
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:tomato-prediction-sqlserver.database.windows.net,1433;"
    "Database=tomato-prediction-db;"
    "Uid=sqladmin;Pwd=REPLACE_ME;"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
)

# ─── Azure Blob Storage ─────────────────────────────────────────────────────
BLOB_STORAGE_CONNECTION_STRING = os.environ.get(
    "TOMATO_BLOB_CONNECTION_STRING",
    "DefaultEndpointsProtocol=https;"
    "AccountName=tomatopredictionstorage;"
    "AccountKey=REPLACE_ME;"
    "EndpointSuffix=core.windows.net",
)
BLOB_CONTAINER_RAW = os.environ.get("TOMATO_BLOB_CONTAINER_RAW", "raw-data")
BLOB_CONTAINER_MODELS = os.environ.get("TOMATO_BLOB_CONTAINER_MODELS", "models")

# ─── Azure Redis Cache ──────────────────────────────────────────────────────
REDIS_HOST = os.environ.get(
    "TOMATO_REDIS_HOST", "tomato-prediction-redis.redis.cache.windows.net"
)
REDIS_PORT = int(os.environ.get("TOMATO_REDIS_PORT", "6380"))
REDIS_PASSWORD = os.environ.get("TOMATO_REDIS_PASSWORD", "REPLACE_ME")
REDIS_SSL = os.environ.get("TOMATO_REDIS_SSL", "true").lower() == "true"

# ─── Azure Key Vault ────────────────────────────────────────────────────────
KEY_VAULT_URL = os.environ.get(
    "TOMATO_KEY_VAULT_URL",
    "https://tomato-prediction-kv.vault.azure.net/",
)

# ─── Azure Application Insights ─────────────────────────────────────────────
APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
    "TOMATO_APPINSIGHTS_KEY", "REPLACE_ME"
)

# ─── Data API (for fetching new market data) ─────────────────────────────────
DATA_API_URL = os.environ.get(
    "TOMATO_DATA_API_URL",
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
)
DATA_API_KEY = os.environ.get("TOMATO_DATA_API_KEY", "REPLACE_ME")

# ─── Model Configuration ────────────────────────────────────────────────────
TARGET_COLUMN = "p_modal"
DATE_COLUMN = "t"
CATEGORICAL_COLUMNS = ["market_id", "market_name", "district_name", "variety"]
NUMERIC_COLUMNS = ["p_min", "p_max"]
LAG_DAYS = [1, 2, 3, 7, 14]
ROLLING_WINDOWS = [3, 7, 14, 30]

# ─── Retraining Thresholds ──────────────────────────────────────────────────
RETRAIN_IMPROVEMENT_THRESHOLD = float(
    os.environ.get("TOMATO_RETRAIN_THRESHOLD", "0.02")
)  # 2 % MAE improvement required to swap models

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("TOMATO_LOG_LEVEL", "INFO").upper()


def setup_logging(name: str = "tomato_pipeline") -> logging.Logger:
    """Return a configured logger that writes to the console."""
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
    log.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    return log


if __name__ == "__main__":
    _log = setup_logging()
    _log.info("Configuration loaded successfully.")
    _log.info("BASE_DIR = %s", BASE_DIR)
    _log.info("RAW_DATA_DIR = %s", RAW_DATA_DIR)
    _log.info("PROCESSED_DATA_DIR = %s", PROCESSED_DATA_DIR)
    _log.info("MODELS_DIR = %s", MODELS_DIR)
