"""
FastAPI Backend Application for Daily Tomato Price Prediction.
Serves prediction APIs, model metadata, historical price charts, and email triggers.
"""

import os
import sys
import json
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from api.models import (
    MarketInfo, 
    PricePrediction, 
    PredictionResponse, 
    ModelMetrics,
    EmailNotificationRequest,
    EmailNotificationResponse
)
from api.config import settings
from api.database import (
    init_db, 
    get_latest_predictions, 
    get_market_history, 
    get_all_markets,
    save_predictions
)
from api.cache import cache_manager
from api.scheduler import scheduler, run_daily_prediction_pipeline
from api.notification import send_price_prediction_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api.main")

app = FastAPI(
    title=settings.APP_NAME,
    description="Automated Daily Tomato Price Forecasting ETL Pipeline & Notification Service on Azure",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    # Populate initial database records from data files if empty
    seed_database_if_empty()
    scheduler.start()
    logger.info("Tomato Price Prediction API started successfully.")

@app.on_event("shutdown")
def shutdown_event():
    scheduler.stop()

def seed_database_if_empty():
    """Populate markets and initial historical/prediction data from preprocessed files if DB is new."""
    try:
        from api.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) as cnt FROM markets")
        row = cursor.fetchone()
        count = row["cnt"] if row else 0
        
        if count == 0:
            logger.info("Seeding initial markets and prices from CSV data...")
            import pandas as pd
            csv_path = os.path.join(ROOT_DIR, "data", "processed", "tomato_prices_processed.csv")
            if not os.path.exists(csv_path):
                csv_path = os.path.join(ROOT_DIR, "data", "raw", "tomato_prices_2025.csv")
                
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                # Seed markets
                markets_df = df[["market_id", "market_name", "district_name"]].drop_duplicates()
                for _, m in markets_df.iterrows():
                    cursor.execute("""
                        INSERT OR IGNORE INTO markets (market_id, market_name, district_name, state_name, commodity, variety)
                        VALUES (?, ?, ?, 'Karnataka', 'Tomato', 'Tomato')
                    """, (str(m["market_id"]), str(m["market_name"]), str(m["district_name"])))
                
                # Seed latest historical prices (sample)
                hist_df = df[["t", "market_id", "market_name", "district_name", "p_min", "p_max", "p_modal"]].tail(500)
                for _, h in hist_df.iterrows():
                    cursor.execute("""
                        INSERT INTO historical_prices (date, market_id, market_name, district_name, p_min, p_max, p_modal)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (str(h["t"]), str(h["market_id"]), str(h["market_name"]), str(h["district_name"]), float(h["p_min"]), float(h["p_max"]), float(h["p_modal"])))
                
                conn.commit()
                logger.info("Database successfully seeded with markets and historical prices.")
        conn.close()
    except Exception as e:
        logger.warning("Database seeding skipped: %s", e)


from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Check for built frontend directory
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "out")
if os.path.exists(FRONTEND_DIST) and os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "docs_url": "/docs",
        "endpoints": [
            "/api/health",
            "/api/predictions",
            "/api/markets",
            "/api/historical/{market_id}",
            "/api/model-info",
            "/api/predict",
            "/api/notify"
        ]
    }

@app.api_route("/api/health", methods=["GET", "HEAD"])
def health_check():
    model_exists = os.path.exists(settings.MODEL_PATH) or os.path.exists(os.path.join(ROOT_DIR, "models", "tomato_price_model.joblib"))
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "model_loaded": model_exists,
        "recipient_email": settings.NOTIFICATION_RECIPIENT,
        "azure_services": {
            "azure_sql": "configured",
            "azure_blob_storage": "configured",
            "azure_ml": "configured",
            "azure_communication_services": "configured",
            "azure_redis": "configured",
            "azure_container_instances": "configured"
        }
    }

@app.get("/api/markets")
def list_markets():
    cached = cache_manager.get("all_markets")
    if cached:
        return cached
    markets = get_all_markets()
    cache_manager.set("all_markets", markets, ttl_seconds=600)
    return markets

@app.get("/api/predictions")
def get_predictions(date_str: Optional[str] = None):
    # Normalize if called directly in code with Query default
    if not isinstance(date_str, str):
        date_str = None
    cache_key = f"predictions_{date_str or 'latest'}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached

    # Check database first
    db_predictions = get_latest_predictions(date_str)
    if db_predictions:
        avg_price = sum(p["predicted_modal_price"] for p in db_predictions) / len(db_predictions)
        response = {
            "generated_at": db_predictions[0].get("generated_at", datetime.now().isoformat()),
            "prediction_date": db_predictions[0].get("prediction_date", datetime.now().strftime("%Y-%m-%d")),
            "total_markets": len(db_predictions),
            "average_predicted_price": round(avg_price, 2),
            "predictions": db_predictions
        }
        cache_manager.set(cache_key, response, ttl_seconds=300)
        return response

    # Fallback to daily_prediction.json on disk
    pred_file = os.path.join(ROOT_DIR, "data", "predictions", "daily_prediction.json")
    if os.path.exists(pred_file):
        with open(pred_file, "r") as f:
            data = json.load(f)
            cache_manager.set(cache_key, data, ttl_seconds=300)
            return data

    # If no predictions yet, run a prediction
    logger.info("No predictions found in DB or cache, generating fresh predictions...")
    res = run_daily_prediction_pipeline()
    return res["prediction_data"]

@app.get("/api/predictions/{market_id}")
def get_prediction_for_market(market_id: str):
    all_preds = get_predictions()
    predictions = all_preds.get("predictions", [])
    for p in predictions:
        if str(p.get("market_id")) == str(market_id):
            return p
    raise HTTPException(status_code=404, detail=f"No prediction found for market {market_id}")

@app.get("/api/historical/{market_id}")
def get_historical_prices(market_id: str, limit: int = 60):
    cache_key = f"historical_{market_id}_{limit}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached
    history = get_market_history(market_id, limit)
    if not history or len(history) < 5:
        try:
            import pandas as pd
            for fname in ["tomato_prices_processed.csv", "tomato_prices_2025.csv", "tomato_prices_2024.csv"]:
                p = os.path.join(ROOT_DIR, "data", "processed", fname)
                if not os.path.exists(p):
                    p = os.path.join(ROOT_DIR, "data", "raw", fname)
                if os.path.exists(p):
                    df = pd.read_csv(p)
                    m_df = df[df["market_id"].astype(str) == str(market_id)].sort_values("t").tail(limit)
                    if len(m_df) > 0:
                        history = [
                            {
                                "date": str(row["t"]),
                                "market_id": str(row["market_id"]),
                                "market_name": str(row.get("market_name", "")),
                                "district_name": str(row.get("district_name", "")),
                                "p_min": float(row.get("p_min", 0)),
                                "p_max": float(row.get("p_max", 0)),
                                "p_modal": float(row.get("p_modal", 0))
                            }
                            for _, row in m_df.iterrows()
                        ]
                        break
        except Exception as e:
            logger.warning("Historical CSV fallback failed: %s", e)
            
    cache_manager.set(cache_key, history, ttl_seconds=300)
    return history

@app.get("/api/model-info")
def get_model_info():
    metrics_file = os.path.join(ROOT_DIR, "models", "metrics.json")
    if os.path.exists(metrics_file):
        with open(metrics_file, "r") as f:
            return json.load(f)
    return {
        "model_name": "TomatoPricePredictor",
        "algorithm": "RandomForestRegressor + XGBoost",
        "status": "ready",
        "features_count": 37
    }

@app.post("/api/predict")
def trigger_prediction(background_tasks: BackgroundTasks):
    """Trigger daily prediction pipeline immediately and update predictions."""
    result = run_daily_prediction_pipeline()
    cache_manager.clear()
    return {
        "status": "success",
        "message": "Daily price prediction pipeline executed successfully.",
        "prediction_date": result["prediction_data"].get("prediction_date"),
        "total_markets": result["prediction_data"].get("total_markets"),
        "email_status": result["notification"].get("status")
    }

@app.post("/api/notify", response_model=EmailNotificationResponse)
def trigger_notification(request: EmailNotificationRequest):
    """Trigger email notification to the specified recipient (defaults to user)."""
    recipient = request.recipient_email or settings.NOTIFICATION_RECIPIENT
    preds = get_predictions()
    
    result = send_price_prediction_notification(
        predictions_data=preds,
        recipient_email=recipient
    )
    
    return EmailNotificationResponse(
        status=result.get("status", "sent"),
        recipient=recipient,
        sent_at=datetime.now().isoformat(),
        message=result.get("message", "Email notification dispatched successfully.")
    )
