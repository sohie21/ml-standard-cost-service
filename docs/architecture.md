# Architecture

## High-level architecture

```text
Developer
  |
  | git push
  v
GitHub Repository
  |
  | GitHub Actions CI
  v
Docker image build validation
  |
  | manual deploy
  v
Cloud VM
  |
  v
Docker Compose
  |
  v
FastAPI service
  |
  | /health
  | /predict
  | /metrics
  v
Model artifact: models/model.joblib
```

## Components

### FastAPI service

Responsible for serving the trained model through REST API.

Endpoints:

- GET /
- GET /health
- GET /metrics
- POST /predict

### Training pipeline

The training pipeline is implemented in `src/train.py`.

It performs:

- data loading
- preprocessing
- feature engineering
- train/test split
- model training
- metric calculation
- model artifact saving
- MLflow experiment logging

### Retraining pipeline

The retraining pipeline is described in `src/pipeline.py` using Prefect.

### Experiment tracking

MLflow is used to log:

- parameters
- metrics
- model artifact

### Infrastructure

Dockerfile describes the container image.

Docker Compose starts the service on the cloud VM.

### CI

GitHub Actions runs:

- dependency installation
- model training
- tests
- Docker image build
