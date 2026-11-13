from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class MarketInfo(BaseModel):
    market_id: str
    market_name: str
    district_name: str
    state_name: str = "Karnataka"
    commodity: str = "Tomato"
    variety: Optional[str] = "Tomato"
    latest_modal_price: Optional[float] = None
    latest_date: Optional[str] = None

class HistoricalPricePoint(BaseModel):
    date: str
    market_id: str
    market_name: str
    district_name: str
    p_min: float
    p_max: float
    p_modal: float

class PricePrediction(BaseModel):
    market_id: str
    market_name: str
    district_name: str
    prediction_date: str
    predicted_modal_price: float
    predicted_min_price: float
    predicted_max_price: float
    confidence_lower: float
    confidence_upper: float
    percentage_change: float
    trend: str  # "UP", "DOWN", "STABLE"

class PredictionResponse(BaseModel):
    generated_at: str
    prediction_date: str
    total_markets: int
    average_predicted_price: float
    predictions: List[PricePrediction]

class ModelMetrics(BaseModel):
    model_name: str
    algorithm: str
    trained_at: str
    mae: float
    rmse: float
    r2_score: float
    training_samples: int
    top_features: Dict[str, float]

class EmailNotificationRequest(BaseModel):
    recipient_email: str
    subject: Optional[str] = None
    markets: Optional[List[str]] = None

class EmailNotificationResponse(BaseModel):
    status: str
    recipient: str
    sent_at: str
    message: str

