"""
Automated Retraining Pipeline
==============================
Designed to run on a daily schedule.  It:

1. Fetches new data (from API or local CSV drop)
2. Re-runs preprocessing on the full dataset
3. Retrains all models
4. Compares the new best model against the currently deployed one
5. Swaps the model only if the new one improves MAE beyond the threshold

Usage
-----
    python retrain_pipeline.py            # run one retraining cycle
    python retrain_pipeline.py --help

Importable API
--------------
    from retrain_pipeline import retrain, fetch_new_data
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    DATA_API_KEY,
    DATA_API_URL,
    DATE_COLUMN,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    RETRAIN_IMPROVEMENT_THRESHOLD,
    TARGET_COLUMN,
    setup_logging,
)
from data_preprocessing import preprocess
from train_model import evaluate_model, get_feature_columns, train_all_models

logger = setup_logging("retrain_pipeline")


# ─── Fetch New Data ─────────────────────────────────────────────────────────

def fetch_new_data(
    raw_dir: Optional[str] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Optional[str]:
    """
    Attempt to pull fresh market data from the government open-data API
    and append it to a CSV in *raw_dir*.

    Returns the path of the new file, or None if no new data was fetched.
    """
    raw_dir = raw_dir or RAW_DATA_DIR
    api_url = api_url or DATA_API_URL
    api_key = api_key or DATA_API_KEY

    if api_key == "REPLACE_ME":
        logger.warning(
            "DATA_API_KEY is not set – skipping live data fetch. "
            "Place new CSVs in %s manually.", raw_dir
        )
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    logger.info("Fetching data for %s → %s from API …", yesterday, today)

    try:
        params = {
            "api-key": api_key,
            "format": "json",
            "filters[state.keyword]": "Karnataka",
            "filters[commodity]": "Tomato",
            "filters[arrival_date]": yesterday,
            "limit": 1000,
        }
        resp = requests.get(api_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        records = data.get("records", [])
        if not records:
            logger.info("API returned 0 records – nothing new.")
            return None

        # Map API fields → our schema
        rows = []
        for r in records:
            rows.append({
                "t": r.get("arrival_date", yesterday),
                "cmdty": "Tomato",
                "market_id": r.get("market_code", ""),
                "market_name": r.get("market", ""),
                "state_id": "29",
                "state_name": "Karnataka",
                "district_id": r.get("district_code", ""),
                "district_name": r.get("district", ""),
                "variety": r.get("variety", "Tomato"),
                "p_min": r.get("min_price", ""),
                "p_max": r.get("max_price", ""),
                "p_modal": r.get("modal_price", ""),
            })

        df_new = pd.DataFrame(rows)
        fname = f"tomato_prices_api_{yesterday.replace('-', '')}.csv"
        out_path = os.path.join(raw_dir, fname)
        df_new.to_csv(out_path, index=False)
        logger.info("Fetched %d new rows → %s", len(df_new), out_path)
        return out_path

    except Exception as exc:
        logger.error("Failed to fetch new data: %s", exc)
        return None


# ─── Compare Models ─────────────────────────────────────────────────────────

def _load_current_metrics() -> dict:
    meta_path = os.path.join(MODELS_DIR, "model_metadata.json")
    if not os.path.exists(meta_path):
        return {}
    with open(meta_path) as f:
        return json.load(f)


# ─── Retrain ─────────────────────────────────────────────────────────────────

def retrain(
    raw_dir: Optional[str] = None,
    force: bool = False,
) -> dict:
    """
    Full retraining cycle.

    Returns a summary dict with keys:
        new_data_fetched, new_metrics, old_metrics, model_updated, reason
    """
    summary: dict = {
        "timestamp": datetime.now().isoformat(),
        "new_data_fetched": False,
        "model_updated": False,
        "reason": "",
    }

    # 1. Fetch
    new_path = fetch_new_data(raw_dir=raw_dir)
    summary["new_data_fetched"] = new_path is not None

    # 2. Preprocess (full dataset)
    logger.info("Running preprocessing on all data in %s …", raw_dir or RAW_DATA_DIR)
    preprocess(raw_dir=raw_dir, save=True)

    # 3. Load old metrics for comparison
    old_meta = _load_current_metrics()
    old_best = old_meta.get("model_name", None)
    old_metrics = (old_meta.get("metrics", {}) or {}).get(old_best, {}) if old_best else {}
    summary["old_metrics"] = old_metrics

    # 4. Backup current model
    latest_path = os.path.join(MODELS_DIR, "best_model_latest.joblib")
    backup_path = os.path.join(MODELS_DIR, "best_model_previous.joblib")
    if os.path.exists(latest_path):
        shutil.copy2(latest_path, backup_path)

    # 5. Train
    result = train_all_models(save=True)
    new_metrics = result["best_metrics"]
    summary["new_metrics"] = new_metrics
    summary["new_best_name"] = result["best_name"]

    # 6. Decide whether to keep the new model
    if not old_metrics or force:
        summary["model_updated"] = True
        summary["reason"] = "No previous model found or force=True; keeping new model."
    else:
        old_mae = old_metrics.get("MAE", float("inf"))
        new_mae = new_metrics.get("MAE", float("inf"))
        improvement = (old_mae - new_mae) / old_mae if old_mae > 0 else 0

        if improvement >= RETRAIN_IMPROVEMENT_THRESHOLD:
            summary["model_updated"] = True
            summary["reason"] = (
                f"New model improved MAE by {improvement:.2%} "
                f"(old={old_mae:.2f}, new={new_mae:.2f}). Threshold={RETRAIN_IMPROVEMENT_THRESHOLD:.0%}."
            )
        else:
            summary["model_updated"] = False
            summary["reason"] = (
                f"New model did not improve MAE enough ({improvement:.2%} < {RETRAIN_IMPROVEMENT_THRESHOLD:.0%}). "
                f"Rolling back."
            )
            # Restore previous model
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, latest_path)
                logger.info("Rolled back to previous model.")

    logger.info("Retrain summary: %s", json.dumps(summary, indent=2))

    # 7. Persist summary log
    log_dir = os.path.join(MODELS_DIR, "retrain_logs")
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"retrain_{ts}.json")
    with open(log_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Retrain log saved to %s", log_path)

    return summary


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Automated retraining pipeline.")
    parser.add_argument("--raw-dir", default=None, help="Raw data directory.")
    parser.add_argument(
        "--force", action="store_true",
        help="Force model update regardless of improvement threshold.",
    )
    args = parser.parse_args()
    retrain(raw_dir=args.raw_dir, force=args.force)


if __name__ == "__main__":
    main()
