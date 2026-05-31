# SLI and SLO

## Technical level

| SLI | SLO | Action |
|---|---:|---|
| Healthcheck availability | /health returns HTTP 200 | Restart container |
| Latency p95 | < 500 ms | Investigate API and model performance |
| 5xx error rate | < 1% | Check logs and rollback if needed |
| Container health | Docker status is healthy | Restart or rebuild service |

## Model level

| SLI | SLO | Action |
|---|---:|---|
| MAE | < 100 | Retrain model |
| RMSE | < 150 | Analyze outliers |
| R2 | > 0.75 | Compare with baseline |
| Data drift | PSI < 0.2 | Retrain model |

## Business level

| SLI | SLO | Action |
|---|---:|---|
| Average standard_cost estimation error | < 100 monetary units | Retrain model |
| Share of high-error predictions | < 5% | Analyze product segments |
| Prediction service availability during business hours | > 99% | Restart service or restore VM |
