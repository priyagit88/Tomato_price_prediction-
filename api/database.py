"""
Database integration for Tomato Price Prediction API.
Supports Azure SQL Database / MSSQL when DATABASE_URL is configured,
with lightweight SQLite fallback for local and containerized operation.
"""

import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("api.database")

DB_FILE = os.getenv("SQLITE_DB_PATH", "./data/tomato_prices.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for markets, historical prices, and daily predictions."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Markets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS markets (
        market_id TEXT PRIMARY KEY,
        market_name TEXT NOT NULL,
        district_name TEXT NOT NULL,
        state_name TEXT DEFAULT 'Karnataka',
        commodity TEXT DEFAULT 'Tomato',
        variety TEXT DEFAULT 'Tomato',
        latest_modal_price REAL,
        latest_date TEXT
    )
    """)
    
    # Historical Prices Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        market_id TEXT NOT NULL,
        market_name TEXT NOT NULL,
        district_name TEXT NOT NULL,
        p_min REAL,
        p_max REAL,
        p_modal REAL,
        FOREIGN KEY (market_id) REFERENCES markets(market_id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_market_date ON historical_prices(market_id, date)")
    
    # Daily Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_date TEXT NOT NULL,
        market_id TEXT NOT NULL,
        market_name TEXT NOT NULL,
        district_name TEXT NOT NULL,
        predicted_modal_price REAL NOT NULL,
        predicted_min_price REAL NOT NULL,
        predicted_max_price REAL NOT NULL,
        confidence_lower REAL NOT NULL,
        confidence_upper REAL NOT NULL,
        percentage_change REAL NOT NULL,
        trend TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        FOREIGN KEY (market_id) REFERENCES markets(market_id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_date ON daily_predictions(prediction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_market ON daily_predictions(market_id)")
    
    # Notifications Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient TEXT NOT NULL,
        sent_at TEXT NOT NULL,
        status TEXT NOT NULL,
        subject TEXT,
        message TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def save_predictions(prediction_data: Dict[str, Any]):
    """Save daily predictions into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    pred_date = prediction_data.get("prediction_date", datetime.now().strftime("%Y-%m-%d"))
    gen_at = prediction_data.get("generated_at", datetime.now().isoformat())
    
    for p in prediction_data.get("predictions", []):
        cursor.execute("""
        INSERT INTO daily_predictions (
            prediction_date, market_id, market_name, district_name,
            predicted_modal_price, predicted_min_price, predicted_max_price,
            confidence_lower, confidence_upper, percentage_change, trend, generated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred_date,
            p["market_id"],
            p["market_name"],
            p["district_name"],
            p["predicted_modal_price"],
            p["predicted_min_price"],
            p["predicted_max_price"],
            p["confidence_lower"],
            p["confidence_upper"],
            p["percentage_change"],
            p["trend"],
            gen_at
        ))
    
    conn.commit()
    conn.close()

def get_latest_predictions(date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    if date_str:
        cursor.execute("SELECT * FROM daily_predictions WHERE prediction_date = ? ORDER BY market_name", (date_str,))
    else:
        cursor.execute("""
        SELECT * FROM daily_predictions 
        WHERE prediction_date = (SELECT MAX(prediction_date) FROM daily_predictions)
        ORDER BY market_name
        """)
        
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_market_history(market_id: str, limit: int = 60) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, market_id, market_name, district_name, p_min, p_max, p_modal
        FROM historical_prices
        WHERE market_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (market_id, limit))
    rows = cursor.fetchall()
    conn.close()
    # return chronologically
    return [dict(r) for r in reversed(rows)]

def get_all_markets() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM markets ORDER BY market_name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_notification(recipient: str, status: str, subject: str, message: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notification_logs (recipient, sent_at, status, subject, message)
        VALUES (?, ?, ?, ?, ?)
    """, (recipient, datetime.now().isoformat(), status, subject, message))
    conn.commit()
    conn.close()

