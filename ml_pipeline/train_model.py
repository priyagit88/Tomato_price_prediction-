"""
Model Training Module
=====================
Trains multiple models (Random Forest, XGBoost, Prophet) on the preprocessed
tomato price data, evaluates them, and saves the best model to disk.

Usage
-----
    python train_model.py                 # train on processed data
    python train_model.py --help          # show options

Importable API
--------------
    from train_model import train_all_models, evaluate_model, get_feature_columns
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    DATE_COLUMN,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    TARGET_COLUMN,
    setup_logging,
)

logger = setup_logging("train_model")


# ─── Feature Selection ──────────────────────────────────────────────────────

# Columns that the models should NOT use as input features
_EXCLUDE_COLS = {
    TARGET_COLUMN,
    DATE_COLUMN,
    "cmdty",
    "state_id",
    "state_name",
    "market_name",
    "district_id",
    "district_name",
    "market_id",
    "variety",
    # raw categoricals are replaced by their _encoded counterparts
}


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of feature columns used for training."""
    return [c for c in df.columns if c not in _EXCLUDE_COLS and df[c].dtype in ("float64", "int64", "int32", "float32", "uint8")]


# ─── Evaluation ──────────────────────────────────────────────────────────────

def evaluate_model(
    y_true: np.ndarray, y_pred: np.ndarray
) -> dict[str, float]:
    """Compute MAE, RMSE, and R² for a set of predictions."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    return {"MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}


# ─── Individual Trainers ────────────────────────────────────────────────────

def _train_random_forest(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_val: pd.DataFrame, y_val: pd.Series,
) -> tuple[Any, dict]:
    logger.info("Training RandomForest …")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    metrics = evaluate_model(y_val.values, preds)
    logger.info("RandomForest  → MAE=%.2f  RMSE=%.2f  R²=%.4f", metrics["MAE"], metrics["RMSE"], metrics["R2"])
    return model, metrics


def _train_xgboost(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_val: pd.DataFrame, y_val: pd.Series,
) -> tuple[Any, dict]:
    logger.info("Training XGBoost …")
    try:
        from xgboost import XGBRegressor
    except ImportError:
        logger.warning("xgboost not installed – skipping XGBoost.")
        return None, {"MAE": float("inf"), "RMSE": float("inf"), "R2": -float("inf")}

    model = XGBRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        n_jobs=-1,
        random_state=42,
        verbosity=0,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    preds = model.predict(X_val)
    metrics = evaluate_model(y_val.values, preds)
    logger.info("XGBoost       → MAE=%.2f  RMSE=%.2f  R²=%.4f", metrics["MAE"], metrics["RMSE"], metrics["R2"])
    return model, metrics


def _train_prophet(
    df_train: pd.DataFrame, df_val: pd.DataFrame,
) -> tuple[Any, dict]:
    """
    Train Facebook Prophet on the market-aggregated daily price.
    Prophet needs columns 'ds' and 'y'.
    """
    logger.info("Training Prophet …")
    try:
        from prophet import Prophet
    except ImportError:
        logger.warning("prophet not installed – skipping Prophet.")
        return None, {"MAE": float("inf"), "RMSE": float("inf"), "R2": -float("inf")}

    # Aggregate to daily level (mean across markets)
    train_ts = (
        df_train.groupby(DATE_COLUMN)[TARGET_COLUMN]
        .mean()
        .reset_index()
        .rename(columns={DATE_COLUMN: "ds", TARGET_COLUMN: "y"})
    )
    val_ts = (
        df_val.groupby(DATE_COLUMN)[TARGET_COLUMN]
        .mean()
        .reset_index()
        .rename(columns={DATE_COLUMN: "ds", TARGET_COLUMN: "y"})
    )

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
    )
    model.fit(train_ts)

    future = model.predict(val_ts[["ds"]])
    preds = future["yhat"].values
    metrics = evaluate_model(val_ts["y"].values, preds)
    logger.info("Prophet       → MAE=%.2f  RMSE=%.2f  R²=%.4f", metrics["MAE"], metrics["RMSE"], metrics["R2"])
    return model, metrics


# ─── Orchestrator ────────────────────────────────────────────────────────────

def train_all_models(
    processed_path: Optional[str] = None,
    save: bool = True,
) -> dict[str, Any]:
    """
    Load processed data, split temporally, train RF / XGB / Prophet,
    pick the best on MAE, and persist it.

    Returns a dict with keys: best_name, best_model, best_metrics,
    all_metrics, feature_columns.
    """
    # ── Load data ───────────────────────────────────────────────────────
    if processed_path is None:
        processed_path = os.path.join(PROCESSED_DATA_DIR, "tomato_prices_processed.csv")
    logger.info("Loading processed data from %s", processed_path)
    df = pd.read_csv(processed_path)
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    df.sort_values(DATE_COLUMN, inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info("Loaded %d rows.", len(df))

    # ── Time-based split (80 / 20) ──────────────────────────────────────
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    logger.info(
        "Train: %d rows (%s → %s) | Val: %d rows (%s → %s)",
        len(df_train),
        df_train[DATE_COLUMN].min().date(),
        df_train[DATE_COLUMN].max().date(),
        len(df_val),
        df_val[DATE_COLUMN].min().date(),
        df_val[DATE_COLUMN].max().date(),
    )

    feature_cols = get_feature_columns(df)
    logger.info("Using %d features: %s", len(feature_cols), feature_cols[:10])

    X_train, y_train = df_train[feature_cols], df_train[TARGET_COLUMN]
    X_val, y_val = df_val[feature_cols], df_val[TARGET_COLUMN]

    # ── Train models ────────────────────────────────────────────────────
    results: dict[str, tuple[Any, dict]] = {}

    model_rf, met_rf = _train_random_forest(X_train, y_train, X_val, y_val)
    results["RandomForest"] = (model_rf, met_rf)

    model_xgb, met_xgb = _train_xgboost(X_train, y_train, X_val, y_val)
    if model_xgb is not None:
        results["XGBoost"] = (model_xgb, met_xgb)

    model_prophet, met_prophet = _train_prophet(df_train, df_val)
    if model_prophet is not None:
        results["Prophet"] = (model_prophet, met_prophet)

    # ── Pick best (lowest MAE) ──────────────────────────────────────────
    best_name = min(results, key=lambda k: results[k][1]["MAE"])
    best_model, best_metrics = results[best_name]
    logger.info("Best model: %s (MAE=%.2f)", best_name, best_metrics["MAE"])

    all_metrics = {name: met for name, (_, met) in results.items()}

    # ── Save ────────────────────────────────────────────────────────────
    if save:
        os.makedirs(MODELS_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Best model artifact
        model_path = os.path.join(MODELS_DIR, f"best_model_{best_name}_{ts}.joblib")
        joblib.dump(best_model, model_path)
        logger.info("Saved best model to %s", model_path)

        # Convenience symlink-like: latest model
        latest_path = os.path.join(MODELS_DIR, "best_model_latest.joblib")
        joblib.dump(best_model, latest_path)

        # Feature list (needed at prediction time)
        meta = {
            "model_name": best_name,
            "trained_at": ts,
            "metrics": all_metrics,
            "feature_columns": feature_cols,
        }
        meta_path = os.path.join(MODELS_DIR, "model_metadata.json")
        with open(meta_path, "w") as fp:
            json.dump(meta, fp, indent=2)
        logger.info("Saved metadata to %s", meta_path)

        # Save all models
        for name, (mdl, _) in results.items():
            p = os.path.join(MODELS_DIR, f"model_{name}_{ts}.joblib")
            joblib.dump(mdl, p)
            logger.info("Saved %s to %s", name, p)

    return {
        "best_name": best_name,
        "best_model": best_model,
        "best_metrics": best_metrics,
        "all_metrics": all_metrics,
        "feature_columns": feature_cols,
    }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Train tomato price models.")
    parser.add_argument(
        "--data",
        default=None,
        help="Path to processed CSV (default: data/processed/tomato_prices_processed.csv).",
    )
    args = parser.parse_args()
    train_all_models(processed_path=args.data, save=True)


if __name__ == "__main__":
    main()
