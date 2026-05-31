# Архитектура ML-системы

## Общая схема

```text
Developer / Colab / VS Code
  ↓
GitHub repository
  ↓
GitHub Actions CI
  ↓
Docker build and tests
  ↓
Yandex Cloud VM
  ↓
Docker container
  ↓
FastAPI prediction service
  ↓
/health, /predict, /metrics, /docs
```

## Жизненный цикл модели

```text
Raw CSV data
  ↓
Data cleaning
  ↓
Feature engineering
  ↓
Train/test split
  ↓
Untrained RandomForestRegressor
  ↓
Model training
  ↓
Offline validation
  ↓
Model artifact
  ↓
Docker image
  ↓
Cloud deployment
  ↓
Online inference
  ↓
Monitoring
  ↓
Retraining decision
```

## Компоненты системы

### Data preparation

Файл:

```text
src/train.py
```

Функции:

- загрузка данных;
- обработка десятичных запятых;
- преобразование дат;
- создание признаков `transaction_month` и `transaction_dayofweek`;
- подготовка категориальных и числовых признаков.

### Model training

Модель:

```text
RandomForestRegressor
```

Pipeline:

```text
ColumnTransformer + OneHotEncoder + RandomForestRegressor
```

Метрики:

```text
MAE
RMSE
R2
```

### Experiment tracking

MLflow используется для логирования:

- параметров модели;
- метрик;
- model artifact.

### Model serving

Файл:

```text
src/app/main.py
```

Сервис:

```text
FastAPI
```

Endpoints:

```text
GET /
GET /health
GET /metrics
POST /predict
GET /docs
```

### Infrastructure

Инфраструктура описана декларативно через:

```text
Dockerfile
docker-compose.yml
```

Если Docker Compose недоступен, сервис может быть запущен напрямую через Docker CLI.

### CI/CD

Файл:

```text
.github/workflows/ci.yml
```

CI выполняет:

1. Установку зависимостей.
2. Обучение модели.
3. Запуск тестов.
4. Сборку Docker image.

### Cloud deployment

Сервис развернут на Yandex Cloud VM.

Публичные endpoints:

```text
http://158.160.138.105:8000/health
http://158.160.138.105:8000/metrics
http://158.160.138.105:8000/docs
http://158.160.138.105:8000/predict
```

## Управление версиями модели

В учебной реализации версия модели задается через:

```text
MODEL_VERSION = "1.0.0"
```

Артефакт модели:

```text
models/model.joblib
```

При появлении новой модели выполняется:

1. Обучение новой модели.
2. Проверка offline-метрик.
3. Сравнение с SLO.
4. Сборка нового Docker image.
5. Перезапуск контейнера.
6. Проверка `/health` и `/metrics`.

## Вывод модели из эксплуатации

Если новая модель не проходит SLO, она не должна заменять текущую production-модель.

Если текущая production-модель перестает соответствовать SLO, выполняется:

1. Проверка качества входных данных.
2. Анализ drift.
3. Запуск retraining pipeline.
4. Сравнение новой модели с текущей.
5. Переключение сервиса на новую модель только при улучшении качества.

В промышленной версии переключение трафика можно реализовать через blue-green deployment или canary deployment. В учебной версии переключение реализуется через замену model artifact и перезапуск Docker container.
