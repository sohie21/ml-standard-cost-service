from pathlib import Path
import time

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from src.app.schemas import PredictionRequest, PredictionResponse


MODEL_PATH = Path("models/model.joblib")
MODEL_VERSION = "1.0.0"

app = FastAPI(
    title="Standard Cost Prediction Service",
    description="ML API for predicting product standard_cost.",
    version=MODEL_VERSION,
)

model_bundle = None


@app.on_event("startup")
def load_model() -> None:
    global model_bundle

    if not MODEL_PATH.exists():
        raise RuntimeError(
            "Model file was not found. Run `python src/train.py` before starting the API."
        )

    model_bundle = joblib.load(MODEL_PATH)


@app.get("/")
def root() -> dict:
    return {
        "service": "standard-cost-prediction",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": model_bundle is not None,
        "model_version": MODEL_VERSION,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    if model_bundle is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    transaction_date = pd.to_datetime(
        payload.transaction_date,
        format="%d.%m.%Y",
        errors="coerce",
    )

    if pd.isna(transaction_date):
        raise HTTPException(
            status_code=422,
            detail="transaction_date must have format DD.MM.YYYY",
        )

    row = pd.DataFrame(
        [
            {
                "product_id": str(payload.product_id),
                "online_order": str(payload.online_order),
                "order_status": payload.order_status,
                "brand": payload.brand,
                "product_line": payload.product_line,
                "product_class": payload.product_class,
                "product_size": payload.product_size,
                "list_price": payload.list_price,
                "transaction_month": transaction_date.month,
                "transaction_dayofweek": transaction_date.dayofweek,
            }
        ]
    )

    model = model_bundle["model"]
    prediction = float(model.predict(row)[0])

    return PredictionResponse(
        predicted_standard_cost=round(prediction, 2),
        model_version=MODEL_VERSION,
    )


@app.get("/metrics")
def metrics() -> dict:
    if model_bundle is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    return {
        "model_version": MODEL_VERSION,
        "offline_metrics": model_bundle.get("metrics", {}),
        "service_slo": {
            "latency_p95_ms": 500,
            "error_rate": "less than 1%",
            "mae_threshold": 100,
        },
    }
