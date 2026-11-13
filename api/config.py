import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Azure Tomato Price Prediction API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Azure SQL / Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./data/tomato_prices.db"
    )
    
    # Redis Cache
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # Azure Communication Services / SendGrid / SMTP
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "smtp") # "azure_communication", "sendgrid", "smtp"
    AZURE_COMMUNICATION_CONNECTION_STRING: str = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "")
    AZURE_COMMUNICATION_SENDER: str = os.getenv("AZURE_COMMUNICATION_SENDER", "DoNotReply@tomato-predictions.azurecomm.net")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    NOTIFICATION_RECIPIENT: str = os.getenv("NOTIFICATION_RECIPIENT", "priya@iservce.onmicrosoft.com")
    
    # Azure Storage / ML
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/tomato_price_model.joblib")
    
    # Paths
    DATA_RAW_DIR: str = os.getenv("DATA_RAW_DIR", "./data/raw")
    DATA_PREDICTIONS_DIR: str = os.getenv("DATA_PREDICTIONS_DIR", "./data/predictions")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

