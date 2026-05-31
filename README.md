# Standard Cost Prediction ML System

This repository contains a small production-like MLOps project for predicting `standard_cost` from transaction data.

## Business goal

The goal is to estimate product standard cost automatically and support margin analytics.

## ML task

Task type: regression.

Target:

```text
standard_cost
```

Main ML metrics:

- MAE
- RMSE
- R2

Main business metric:

- average absolute standard cost estimation error

## MLOps maturity level

Declared maturity level: 2.

Implemented components:

- code versioning through GitHub
- CI through GitHub Actions
- model serving through FastAPI
- Dockerized deployment
- Docker Compose infrastructure
- model experiment logging through MLflow
- retraining pipeline description through Prefect
- healthcheck endpoint
- metrics endpoint
- SLI/SLO documentation
- ADR for Metrics Driven Development

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/train.py
pytest -q
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

## Docker run

```bash
docker compose up -d --build
docker ps
curl http://localhost:8000/health
```

## Prediction example

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 2,
    "online_order": false,
    "order_status": "Approved",
    "brand": "Solex",
    "product_line": "Standard",
    "product_class": "medium",
    "product_size": "medium",
    "list_price": 71.49,
    "transaction_date": "25.02.2017"
  }'
```

## Cloud deployment

On cloud VM:

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/YOUR_USERNAME/ml-standard-cost-service.git
cd ml-standard-cost-service

bash scripts/bootstrap_vm.sh
newgrp docker

bash scripts/deploy_vm.sh
```

Then open:

```text
http://YOUR_VM_PUBLIC_IP:8000/health
http://YOUR_VM_PUBLIC_IP:8000/docs
```

## Destroy infrastructure

```bash
bash scripts/destroy.sh
```

If the VM is no longer needed, delete it in the cloud provider console.
