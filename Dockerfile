# =============================================================================
# Dockerfile - Production Container for Tomato Price Prediction API
# =============================================================================

# --------------- Stage 1: Builder ---------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install wheels
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --------------- Stage 2: Runtime ---------------
FROM python:3.11-slim AS runtime

LABEL maintainer="tomato-price-prediction-team"
LABEL description="Tomato Price Prediction ML API Service"
LABEL version="1.0.0"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application directories
COPY api/ ./api/
COPY ml_pipeline/ ./ml_pipeline/
COPY data/ ./data/
COPY models/ ./models/
COPY frontend/out/ ./frontend/out/

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    MODEL_PATH=/app/models/tomato_price_model.joblib \
    DATA_PATH=/app/data \
    LOG_LEVEL=INFO

# Ensure directory permissions
RUN mkdir -p /app/logs /app/data/predictions \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
