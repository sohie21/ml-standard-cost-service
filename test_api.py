from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from src.app.main import app


def ensure_model_exists():
    model_path = Path("models/model.joblib")
    if not model_path.exists():
        subprocess.run([sys.executable, "src/train.py"], check=True)


def test_health_endpoint():
    ensure_model_exists()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True


def test_predict_endpoint():
    ensure_model_exists()

    payload = {
        "product_id": 2,
        "online_order": False,
        "order_status": "Approved",
        "brand": "Solex",
        "product_line": "Standard",
        "product_class": "medium",
        "product_size": "medium",
        "list_price": 71.49,
        "transaction_date": "25.02.2017"
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "predicted_standard_cost" in body
    assert isinstance(body["predicted_standard_cost"], float)
