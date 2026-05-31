# SLI и SLO для Standard Cost Prediction Service

## Назначение документа

Документ описывает Service Level Indicators и Service Level Objectives для ML-системы, которая предсказывает `standard_cost`.

Критерии описаны на трех уровнях:

1. Технический уровень.
2. Модельный уровень.
3. Бизнес-уровень.

Так как задача является регрессионной, вместо классификационных метрик `AUC`, `Precision` и `Recall` используются `MAE`, `RMSE` и `R2`. Drift используется как универсальный показатель изменения распределения данных.

## Технический уровень

| Область | SLI | SLO | Критический уровень | Как измеряется | Действие при нарушении |
|---|---|---:|---:|---|---|
| Availability | `/health` availability | HTTP 200 | недоступен 5 минут | `curl /health`, Docker healthcheck | перезапустить контейнер |
| Latency | Prediction latency p95 | < 500 ms | > 1000 ms 10 минут | API logs или monitoring | проверить API и модель |
| Errors | 5xx error rate | < 1% | > 5% 10 минут | API logs | rollback или restart |
| CPU | CPU utilization | < 70% average | > 90% 10 минут | VM metrics | оптимизация или увеличение VM |
| Memory | RAM utilization | < 75% average | > 90% 10 минут | VM metrics | restart или увеличение RAM |
| Container | Docker container health | `healthy` | `unhealthy` | `docker ps` | rebuild/restart container |

## Модельный уровень

| Область | SLI | SLO | Критический уровень | Как измеряется | Действие при нарушении |
|---|---|---:|---:|---|---|
| Regression quality | MAE | < 100 | > 150 | offline validation set | retrain model |
| Regression quality | RMSE | < 150 | > 250 | offline validation set | analyze outliers and retrain |
| Regression quality | R2 | > 0.75 | < 0.50 | offline validation set | compare with baseline |
| Data drift | PSI for `list_price` | < 0.2 | > 0.3 | train vs production distribution | retrain model |
| Category drift | new/rare categories in `brand` | < 20% | > 40% | production input logs | update training data |
| Prediction drift | mean predicted `standard_cost` shift | < 20% | > 40% | prediction distribution | investigate data quality |

## Бизнес-уровень

| Область | SLI | SLO | Критический уровень | Как измеряется | Действие при нарушении |
|---|---|---:|---:|---|---|
| Cost estimation quality | Average absolute cost estimation error | < 100 monetary units | > 150 | predicted vs actual `standard_cost` | retrain model |
| High-risk predictions | Share of predictions with error > 200 | < 5% | > 10% | post-factum validation | analyze weak segments |
| Margin analytics | Correct margin band estimation | > 90% | < 80% | compare predicted and actual margin band | adjust features/model |
| Business availability | API availability during defense/business hours | > 99% | < 95% | healthcheck logs | restore VM/service |
| Manual work reduction | Share of transactions processed automatically | > 95% | < 80% | API request logs | investigate failed requests |

## Логика реагирования

Если нарушен технический SLO:

1. Проверить `/health`.
2. Проверить `docker ps`.
3. Проверить container logs.
4. Перезапустить контейнер.
5. При необходимости пересобрать Docker image.

Если нарушен модельный SLO:

1. Проверить качество входных данных.
2. Сравнить production data с training data.
3. Запустить retraining pipeline.
4. Сравнить новую модель с текущей.
5. Переключить сервис на новую модель только если она лучше текущей.

Если нарушен бизнес-SLO:

1. Разбить ошибки по `brand`, `product_line`, `product_class`, `product_size`.
2. Найти слабые сегменты.
3. Добавить данные или признаки.
4. Переобучить модель.
5. Проверить новую модель на offline validation.
