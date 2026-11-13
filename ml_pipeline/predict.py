"""
Prediction Module
=================
Loads the best trained model and generates next-day price predictions
for one or all markets.

Usage
-----
    python predict.py                            # predict all markets, tomorrow
    python predict.py --market-id 108 --date 2025-11-01
    python predict.py --help

Importable API
--------------
    from predict import load_model, predict_market, predict_all_markets
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    CATEGORICAL_COLUMNS,
    DATE_COLUMN,
    LAG_DAYS,
    MODELS_DIR,
    PREDICTIONS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    ROLLING_WINDOWS,
    TARGET_COLUMN,
    setup_logging,
)

logger = setup_logging("predict")


# ─── Load Artefacts ──────────────────────────────────────────────────────────

def load_model(
    model_path: Optional[str] = None,
    meta_path: Optional[str] = None,
    encoder_path: Optional[str] = None,
) -> tuple[Any, dict, dict]:
    """Return (model, metadata_dict, label_encoders)."""
    model_path = model_path or os.path.join(MODELS_DIR, "best_model_latest.joblib")
    meta_path = meta_path or os.path.join(MODELS_DIR, "model_metadata.json")
    encoder_path = encoder_path or os.path.join(PROCESSED_DATA_DIR, "label_encoders.joblib")

    logger.info("Loading model from %s", model_path)
    model = joblib.load(model_path)

    with open(meta_path) as f:
        metadata = json.load(f)

    encoders: dict = {}
    if os.path.exists(encoder_path):
        encoders = joblib.load(encoder_path)

    return model, metadata, encoders


# ─── Build Feature Row ──────────────────────────────────────────────────────

def _build_feature_row(
    market_id: str,
    target_date: datetime,
    history_df: pd.DataFrame,
    encoders: dict,
    feature_columns: list[str],
) -> pd.DataFrame:
    """
    Construct a single-row DataFrame with the same features the model was
    trained on, using *history_df* (all historical rows for this market) to
    compute lags and rolling stats.
    """
    market_hist = history_df[history_df["market_id"] == str(market_id)].copy()
    market_hist[DATE_COLUMN] = pd.to_datetime(market_hist[DATE_COLUMN])
    market_hist.sort_values(DATE_COLUMN, inplace=True)

    row: dict[str, Any] = {}

    # Calendar features
    row["day_of_week"] = target_date.weekday()
    row["day_of_month"] = target_date.day
    row["month"] = target_date.month
    row["year"] = target_date.year
    row["week_of_year"] = target_date.isocalendar()[1]
    row["is_weekend"] = int(target_date.weekday() >= 5)

    # Latest available prices
    if not market_hist.empty:
        latest = market_hist.iloc[-1]
        row["p_min"] = float(latest.get("p_min", 0))
        row["p_max"] = float(latest.get("p_max", 0))
        row["price_spread"] = row["p_max"] - row["p_min"]
        modal = float(latest.get(TARGET_COLUMN, 0))
        row["price_spread_pct"] = row["price_spread"] / modal if modal else 0
    else:
        row["p_min"] = row["p_max"] = 0
        row["price_spread"] = row["price_spread_pct"] = 0

    # Lag features
    prices = market_hist[TARGET_COLUMN].astype(float).values
    for lag in LAG_DAYS:
        row[f"lag_{lag}"] = float(prices[-lag]) if len(prices) >= lag else 0.0

    # Rolling features
    for window in ROLLING_WINDOWS:
        tail = prices[-window:] if len(prices) >= window else prices
        if len(tail) > 0:
            row[f"rolling_mean_{window}"] = float(np.mean(tail))
            row[f"rolling_std_{window}"] = float(np.std(tail))
            row[f"rolling_min_{window}"] = float(np.min(tail))
            row[f"rolling_max_{window}"] = float(np.max(tail))
        else:
            row[f"rolling_mean_{window}"] = 0
            row[f"rolling_std_{window}"] = 0
            row[f"rolling_min_{window}"] = 0
            row[f"rolling_max_{window}"] = 0

    # Price momentum
    row["price_change_1d"] = float(prices[-1] - prices[-2]) if len(prices) >= 2 else 0
    row["price_change_7d"] = float(prices[-1] - prices[-8]) if len(prices) >= 8 else 0

    # Encoded categoricals
    for col in CATEGORICAL_COLUMNS:
        if col in encoders and f"{col}_encoded" in feature_columns:
            le = encoders[col]
            val = str(market_id) if col == "market_id" else str(latest.get(col, "UNKNOWN")) if not market_hist.empty else "UNKNOWN"
            known = set(le.classes_)
            if val not in known:
                val = "UNKNOWN"
                if "UNKNOWN" not in known:
                    le.classes_ = np.append(le.classes_, "UNKNOWN")
            row[f"{col}_encoded"] = le.transform([val])[0]

    # Build a DataFrame aligned to the expected features
    feature_row = pd.DataFrame([row])
    for c in feature_columns:
        if c not in feature_row.columns:
            feature_row[c] = 0
    feature_row = feature_row[feature_columns]

    return feature_row


# ─── Predict ─────────────────────────────────────────────────────────────────

def predict_market(
    market_id: str,
    target_date: datetime,
    model: Any = None,
    metadata: Optional[dict] = None,
    encoders: Optional[dict] = None,
    history_df: Optional[pd.DataFrame] = None,
) -> dict:
    """Predict the modal price for a single market on *target_date*."""
    if model is None:
        model, metadata, encoders = load_model()
    if history_df is None:
        history_df = pd.read_csv(
            os.path.join(PROCESSED_DATA_DIR, "tomato_prices_processed.csv")
        )
    feature_cols = metadata["feature_columns"]

    features = _build_feature_row(
        market_id, target_date, history_df, encoders, feature_cols,
    )
    prediction = float(model.predict(features)[0])

    return {
        "market_id": market_id,
        "date": target_date.strftime("%Y-%m-%d"),
        "predicted_p_modal": round(prediction, 2),
        "model": metadata.get("model_name", "unknown"),
    }


def predict_all_markets(
    target_date: Optional[datetime] = None,
    save: bool = True,
) -> pd.DataFrame:
    """
    Predict next-day price for every market present in the processed data.
    """
    model, metadata, encoders = load_model()
    history_df = pd.read_csv(
        os.path.join(PROCESSED_DATA_DIR, "tomato_prices_processed.csv")
    )
    if target_date is None:
        latest_date = pd.to_datetime(history_df[DATE_COLUMN]).max()
        target_date = latest_date + timedelta(days=1)
    logger.info("Predicting for date: %s", target_date.strftime("%Y-%m-%d"))

    market_ids = history_df["market_id"].astype(str).unique()
    logger.info("Markets to predict: %d", len(market_ids))

    predictions: list[dict] = []
    for mid in market_ids:
        try:
            pred = predict_market(
                mid, target_date, model, metadata, encoders, history_df,
            )
            # Also grab the market name for readability
            mkt_rows = history_df[history_df["market_id"] == mid]
            if not mkt_rows.empty and "market_name" in mkt_rows.columns:
                pred["market_name"] = mkt_rows["market_name"].iloc[0]
            predictions.append(pred)
        except Exception as exc:
            logger.warning("Failed for market %s: %s", mid, exc)

    df_preds = pd.DataFrame(predictions)
    if save and not df_preds.empty:
        os.makedirs(PREDICTIONS_DIR, exist_ok=True)
        fname = f"predictions_{target_date.strftime('%Y%m%d')}.csv"
        out_path = os.path.join(PREDICTIONS_DIR, fname)
        df_preds.to_csv(out_path, index=False)
        logger.info("Saved %d predictions to %s", len(df_preds), out_path)

        # Build market lookup mapping from raw or processed data
        market_meta = {}
        for raw_f in sorted(glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))):
            try:
                m_df = pd.read_csv(raw_f, dtype=str)
                for _, r in m_df[["market_id", "market_name", "district_name"]].drop_duplicates().iterrows():
                    market_meta[str(r["market_id"])] = {
                        "market_name": str(r["market_name"]),
                        "district_name": str(r["district_name"])
                    }
            except Exception:
                pass

        # Build comprehensive json for API, frontend, and email notification
        pred_items = []
        for p in predictions:
            mid = str(p["market_id"])
            meta = market_meta.get(mid, {})
            mkt_name = meta.get("market_name") or p.get("market_name") or f"Market {mid}"
            dist_name = meta.get("district_name") or "Karnataka"
            
            mkt_rows = history_df[history_df["market_id"].astype(str) == mid]
            pred_val = p["predicted_p_modal"]
            prev_price = float(mkt_rows["p_modal"].iloc[-1]) if not mkt_rows.empty else pred_val
            diff = pred_val - prev_price
            pct_chg = round((diff / prev_price * 100), 2) if prev_price > 0 else 0.0
            trend = "UP" if pct_chg > 1.0 else ("DOWN" if pct_chg < -1.0 else "STABLE")
            
            pred_items.append({
                "market_id": mid,
                "market_name": mkt_name,
                "district_name": dist_name,
                "prediction_date": target_date.strftime("%Y-%m-%d"),
                "predicted_modal_price": round(pred_val, 2),
                "predicted_min_price": round(pred_val * 0.90, 2),
                "predicted_max_price": round(pred_val * 1.10, 2),
                "confidence_lower": round(pred_val * 0.93, 2),
                "confidence_upper": round(pred_val * 1.07, 2),
                "percentage_change": pct_chg,
                "trend": trend,
            })

        avg_p = sum(item["predicted_modal_price"] for item in pred_items) / len(pred_items) if pred_items else 0.0
        json_payload = {
            "generated_at": datetime.now().isoformat(),
            "prediction_date": target_date.strftime("%Y-%m-%d"),
            "total_markets": len(pred_items),
            "average_predicted_price": round(avg_p, 2),
            "predictions": pred_items
        }
        
        json_path = os.path.join(PREDICTIONS_DIR, "daily_prediction.json")
        with open(json_path, "w") as f:
            import json
            json.dump(json_payload, f, indent=2)
        logger.info("Saved JSON predictions to %s", json_path)

    return df_preds


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Predict tomato prices.")
    parser.add_argument("--market-id", default=None, help="Predict a single market.")
    parser.add_argument("--date", default=None, help="Target date (YYYY-MM-DD). Defaults to tomorrow.")
    args = parser.parse_args()

    target = datetime.strptime(args.date, "%Y-%m-%d") if args.date else None

    if args.market_id:
        model, metadata, encoders = load_model()
        target = target or (datetime.now() + timedelta(days=1))
        result = predict_market(args.market_id, target, model, metadata, encoders)
        logger.info("Prediction: %s", result)
    else:
        predict_all_markets(target_date=target, save=True)


if __name__ == "__main__":
    main()
