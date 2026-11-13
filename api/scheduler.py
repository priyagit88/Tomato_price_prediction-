"""
Daily Prediction & Email Automation Scheduler.
Automates daily ETL inference and email notification dispatch.
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
from typing import Optional

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from api.database import save_predictions, get_latest_predictions, log_notification
from api.notification import send_price_prediction_notification
from api.config import settings

logger = logging.getLogger("api.scheduler")

def run_daily_prediction_pipeline(recipient: Optional[str] = None):
    """
    Executes the daily inference pipeline:
    1. Runs ML predict script across all markets.
    2. Stores predicted prices in the database.
    3. Sends notification email with daily market predictions to the user.
    """
    recipient = recipient or settings.NOTIFICATION_RECIPIENT
    logger.info("Starting automated daily prediction pipeline for %s...", recipient)
    
    try:
        from ml_pipeline.predict import predict_all_markets
        predictions_data = predict_all_markets()
    except Exception as e:
        logger.warning("Falling back to ml_pipeline script execution: %s", e)
        import subprocess
        result = subprocess.run([sys.executable, "ml_pipeline/predict.py"], capture_output=True, text=True, cwd=ROOT_DIR)
        logger.info("Predict output: %s", result.stdout)
        
        # Load the generated json
        import json
        pred_file = os.path.join(ROOT_DIR, "data", "predictions", "daily_prediction.json")
        if os.path.exists(pred_file):
            with open(pred_file, "r") as f:
                predictions_data = json.load(f)
        else:
            raise RuntimeError(f"Predictions file not found at {pred_file}")

    # 2. Save into Database
    try:
        save_predictions(predictions_data)
        logger.info("Successfully persisted daily predictions to database.")
    except Exception as e:
        logger.error("Failed to persist predictions to DB: %s", e)

    # 3. Send Email Notification
    email_result = send_price_prediction_notification(
        predictions_data=predictions_data,
        recipient_email=recipient
    )
    
    log_notification(
        recipient=recipient,
        status=email_result.get("status", "unknown"),
        subject=f"Daily Tomato Price Forecast - {predictions_data.get('prediction_date')}",
        message=email_result.get("message", "")
    )
    
    logger.info("Automated daily prediction pipeline finished: %s", email_result)
    return {
        "prediction_data": predictions_data,
        "notification": email_result
    }

class BackgroundScheduler:
    """Lightweight daemon thread for daily scheduled runs."""
    def __init__(self, target_hour: int = 6, target_minute: int = 0):
        self.target_hour = target_hour
        self.target_minute = target_minute
        self.running = False
        self._thread = None

    def _loop(self):
        logger.info("Daily prediction background scheduler active (trigger at %02d:%02d IST/UTC).", self.target_hour, self.target_minute)
        last_run_day = None
        while self.running:
            now = datetime.now()
            if now.hour == self.target_hour and now.minute == self.target_minute and now.day != last_run_day:
                last_run_day = now.day
                try:
                    run_daily_prediction_pipeline()
                except Exception as e:
                    logger.error("Error in scheduled daily prediction: %s", e)
            time.sleep(30)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False

scheduler = BackgroundScheduler()

