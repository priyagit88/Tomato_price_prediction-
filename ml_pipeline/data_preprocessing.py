"""
Data Preprocessing Module
=========================
Loads raw CSV files, cleans data, engineers features, encodes categoricals,
handles missing values, and saves the result to the processed-data directory.

Usage
-----
    python data_preprocessing.py          # process all CSVs in data/raw
    python data_preprocessing.py --help   # show options

Importable API
--------------
    from data_preprocessing import load_raw_data, preprocess, engineer_features
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Ensure the ml_pipeline package is importable when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    CATEGORICAL_COLUMNS,
    DATE_COLUMN,
    LAG_DAYS,
    NUMERIC_COLUMNS,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    ROLLING_WINDOWS,
    TARGET_COLUMN,
    setup_logging,
)

logger = setup_logging("data_preprocessing")


# ─── Load ────────────────────────────────────────────────────────────────────

def load_raw_data(raw_dir: Optional[str] = None) -> pd.DataFrame:
    """Load and concatenate every CSV in *raw_dir* into a single DataFrame."""
    raw_dir = raw_dir or RAW_DATA_DIR
    csv_files = sorted(glob.glob(os.path.join(raw_dir, "*.csv")))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    frames: list[pd.DataFrame] = []
    for f in csv_files:
        logger.info("Loading %s", f)
        df = pd.read_csv(f, dtype=str)
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Loaded %d rows from %d files.", len(combined), len(csv_files))
    return combined


# ─── Clean ───────────────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: types, duplicates, nulls."""
    df = df.copy()

    # Parse date
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    df.dropna(subset=[DATE_COLUMN], inplace=True)

    # Numeric columns
    for col in [TARGET_COLUMN] + NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where the target is missing
    df.dropna(subset=[TARGET_COLUMN], inplace=True)

    # Fill remaining numeric NaNs with column median
    for col in NUMERIC_COLUMNS:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.info("Filled %s NaNs with median %.2f", col, median_val)

    # Drop exact duplicates
    before = len(df)
    df.drop_duplicates(inplace=True)
    dropped = before - len(df)
    if dropped:
        logger.info("Dropped %d duplicate rows.", dropped)

    # Ensure market_id is string for grouping
    df["market_id"] = df["market_id"].astype(str)

    # Sort chronologically per market
    df.sort_values([DATE_COLUMN, "market_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    logger.info("Cleaned data: %d rows, %d columns.", *df.shape)
    return df


# ─── Feature Engineering ────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar, lag, and rolling-average features."""
    df = df.copy()

    # Calendar features
    df["day_of_week"] = df[DATE_COLUMN].dt.dayofweek
    df["day_of_month"] = df[DATE_COLUMN].dt.day
    df["month"] = df[DATE_COLUMN].dt.month
    df["year"] = df[DATE_COLUMN].dt.year
    df["week_of_year"] = df[DATE_COLUMN].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Price spread
    df["price_spread"] = df["p_max"] - df["p_min"]
    df["price_spread_pct"] = np.where(
        df["p_modal"] > 0, df["price_spread"] / df["p_modal"], 0
    )

    # Lag and rolling features (per market)
    for lag in LAG_DAYS:
        df[f"lag_{lag}"] = df.groupby("market_id")[TARGET_COLUMN].shift(lag)

    for window in ROLLING_WINDOWS:
        grp = df.groupby("market_id")[TARGET_COLUMN]
        df[f"rolling_mean_{window}"] = grp.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).mean()
        )
        df[f"rolling_std_{window}"] = grp.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).std()
        )
        df[f"rolling_min_{window}"] = grp.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).min()
        )
        df[f"rolling_max_{window}"] = grp.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).max()
        )

    # Price momentum (day-over-day change)
    df["price_change_1d"] = df.groupby("market_id")[TARGET_COLUMN].diff(1)
    df["price_change_7d"] = df.groupby("market_id")[TARGET_COLUMN].diff(7)

    # Fill remaining NaNs from lag/rolling with 0 (early rows)
    lag_roll_cols = [c for c in df.columns if c.startswith(("lag_", "rolling_", "price_change_"))]
    df[lag_roll_cols] = df[lag_roll_cols].fillna(0)

    logger.info("Engineered %d features.", len(lag_roll_cols) + 6)
    return df


# ─── Encode Categoricals ────────────────────────────────────────────────────

def encode_categoricals(
    df: pd.DataFrame,
    encoders: Optional[dict[str, LabelEncoder]] = None,
) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    """
    Label-encode categorical columns. If *encoders* is supplied they are
    re-used (for prediction time); otherwise new encoders are fitted.
    """
    df = df.copy()
    if encoders is None:
        encoders = {}

    cols_to_encode = [c for c in CATEGORICAL_COLUMNS if c in df.columns]
    for col in cols_to_encode:
        df[col] = df[col].astype(str)
        if col not in encoders:
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col])
            encoders[col] = le
        else:
            le = encoders[col]
            # Handle unseen labels gracefully
            known = set(le.classes_)
            df[col] = df[col].apply(lambda v: v if v in known else "UNKNOWN")
            if "UNKNOWN" not in known:
                le.classes_ = np.append(le.classes_, "UNKNOWN")
            df[f"{col}_encoded"] = le.transform(df[col])

    logger.info("Encoded %d categorical columns.", len(cols_to_encode))
    return df, encoders


# ─── Full Pipeline ───────────────────────────────────────────────────────────

def preprocess(
    raw_dir: Optional[str] = None,
    save: bool = True,
) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    """Run the full preprocessing pipeline and optionally save to disk."""
    df = load_raw_data(raw_dir)
    df = clean_data(df)
    df = engineer_features(df)
    df, encoders = encode_categoricals(df)

    if save:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        out_path = os.path.join(PROCESSED_DATA_DIR, "tomato_prices_processed.csv")
        df.to_csv(out_path, index=False)
        logger.info("Saved processed data to %s (%d rows).", out_path, len(df))

        # Persist encoders
        import joblib
        enc_path = os.path.join(PROCESSED_DATA_DIR, "label_encoders.joblib")
        joblib.dump(encoders, enc_path)
        logger.info("Saved label encoders to %s", enc_path)

    return df, encoders


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess tomato price data.")
    parser.add_argument(
        "--raw-dir",
        default=RAW_DATA_DIR,
        help="Directory containing raw CSV files.",
    )
    args = parser.parse_args()
    preprocess(raw_dir=args.raw_dir, save=True)


if __name__ == "__main__":
    main()
