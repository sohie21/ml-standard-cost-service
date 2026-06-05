# Standard Cost Prediction ML System

## Описание репозитория, бизнес-концепция и структура проекта

Этот репозиторий содержит учебную production-like ML-систему для предсказания `standard_cost` по данным о транзакциях велосипедного магазина.

Бизнес-идея проекта: автоматически оценивать себестоимость товара на основе признаков транзакции и товара. Такая система может использоваться для быстрой оценки маржинальности, поиска аномальных транзакций и поддержки решений по ценообразованию.

Целевая переменная:

```text
standard_cost
```

Репозиторий:

```text
https://github.com/sohie21/ml-standard-cost-service
```

Развернутый облачный сервис:

```text
http://158.160.138.105:8000/docs
```

Структура проекта:

```text
.
├── .github/workflows/ci.yml          # CI pipeline: обучение, тесты, сборка Docker image
├── data/transactions.csv             # учебный мини-датасет транзакций
├── docs/
│   ├── architecture.md               # описание архитектуры ML-системы
│   ├── manifest.md                   # ML-манифест проекта
│   └── adr/
│       └── 001-latency-mdd.md        # ADR по Metrics Driven Development
├── monitoring/
│   └── sli_slo.md                    # SLI/SLO на техническом, модельном и бизнес-уровнях
├── scripts/
│   ├── bootstrap_vm.sh               # установка инфраструктурных зависимостей на VM
│   ├── deploy_vm.sh                  # запуск сервиса через Docker
│   └── destroy.sh                    # деинсталляция инфраструктуры проекта
├── src/
│   ├── train.py                      # обучение модели и сохранение артефакта
│   ├── pipeline.py                   # retraining pipeline через Prefect
│   └── app/
│       ├── main.py                   # FastAPI service
│       └── schemas.py                # схемы входных и выходных данных API
├── tests/
│   └── test_api.py                   # тесты API
├── Dockerfile                        # описание Docker image
├── docker-compose.yml                # декларативное описание запуска сервиса
├── requirements.txt                  # Python dependencies
└── README.md                         # основной документ проекта
```

## Краткое описание ML-блока

Тип задачи: регрессия.

Модель предсказывает числовое значение `standard_cost`. Это не классификация, поэтому вместо `AUC`, `Precision` и `Recall` по критериям используются регрессионные метрики: `MAE`, `RMSE` и `R2`.

Используемые признаки:

```text
product_id
online_order
order_status
brand
product_line
product_class
product_size
list_price
transaction_month
transaction_dayofweek
```

Неиспользуемые признаки:

```text
transaction_id
customer_id
transaction_date в сыром виде
```

`transaction_id` является техническим идентификатором транзакции. `customer_id` в учебной версии не используется как основной бизнес-признак, чтобы не делать модель зависимой от конкретных клиентов. Из `transaction_date` извлекаются признаки `transaction_month` и `transaction_dayofweek`.

Основной pipeline обучения:

1. Загрузка данных.
2. Очистка числовых значений с десятичной запятой.
3. Преобразование даты.
4. Генерация календарных признаков.
5. One-Hot Encoding категориальных признаков.
6. Обучение `RandomForestRegressor`.
7. Расчет `MAE`, `RMSE`, `R2`.
8. Сохранение модели в `models/model.joblib`.
9. Логирование эксперимента через MLflow.

## MLOps maturity level

Заявленный уровень зрелости ML-системы: **Level 2** по классификации MLOps maturity levels.

| Компонент | Реализация в проекте |
|---|---|
| Source control | GitHub repository |
| CI | GitHub Actions |
| Test and build services | `pytest`, Docker build в CI |
| Deployment service | Docker/Docker Compose на Yandex Cloud VM |
| Model serving | FastAPI REST API |
| Model artifact | `models/model.joblib`, создается при сборке Docker image |
| Metadata / experiment tracking | MLflow logging в `src/train.py` |
| Pipeline orchestrator | Prefect flow в `src/pipeline.py` |
| Monitoring endpoint | `/health`, `/metrics` |
| SLI/SLO | `monitoring/sli_slo.md` |
| MDD / ADR | `docs/adr/001-latency-mdd.md` |

### Жизненный цикл ML-пайплайна

Архитектура пайплайна обслуживает полный жизненный цикл модели:

```text
Raw data
  ↓
Data validation and cleaning
  ↓
Feature engineering
  ↓
Untrained model
  ↓
Training
  ↓
Offline validation
  ↓
Model artifact
  ↓
Container build
  ↓
Cloud deployment
  ↓
Online inference
  ↓
Monitoring
  ↓
Retraining decision
  ↓
Traffic switch to new model version
```

Подробно:

1. **Очистка данных.** В `src/train.py` выполняется загрузка CSV, обработка десятичных запятых, преобразование дат и удаление строк с критическими пропусками.
2. **Подача данных в необученную модель.** После preprocessing данные передаются в `RandomForestRegressor`.
3. **Обучение модели.** Модель обучается на train split.
4. **Оценка качества.** На test split рассчитываются `MAE`, `RMSE`, `R2`.
5. **Валидация модели.** Если метрики хуже SLO, модель не должна продвигаться в production.
6. **Сохранение артефакта.** Обученная модель сохраняется в `models/model.joblib`.
7. **Сборка сервиса.** Docker image содержит код API и модель.
8. **Сервинг модели.** FastAPI предоставляет `/predict`, `/health`, `/metrics`, `/docs`.
9. **Мониторинг.** Проверяется доступность сервиса, latency, ошибки, offline-метрики модели.
10. **Вывод плохой модели из эксплуатации.** Если новая модель не проходит SLO, трафик остается на текущей версии. Если новая модель лучше, происходит переключение сервиса на новый артефакт модели через пересборку и перезапуск контейнера.

В учебной реализации переключение трафика выполняется через замену model artifact и перезапуск Docker container

## Проверка облачного развертывания на VM

Сервис развернут на Yandex Cloud VM и доступен по публичному адресу.

Swagger / API documentation:

```text
http://130.193.57.112:8000/docs
```

Healthcheck:

```text
http://130.193.57.112:8000/health
```

Metrics / validation endpoint:

```text
http://130.193.57.112:8000/metrics
```

Prediction endpoint:

```text
http://130.193.57.112:8000/predict
```

Проверка из терминала:

```bash
curl http://130.193.57.112:8000/health
curl http://130.193.57.112:8000/metrics
```

Пример запроса к модели:

```bash
curl -X POST http://130.193.57.112:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{{ 
    "product_id": 2,
    "online_order": false,
    "order_status": "Approved",
    "brand": "Solex",
    "product_line": "Standard",
    "product_class": "medium",
    "product_size": "medium",
    "list_price": 71.49,
    "transaction_date": "25.02.2017"
  }}'
```

Проверка контейнера на VM:

```bash
sudo docker ps
```

Ожидаемый результат: контейнер `standard-cost-api` находится в состоянии `Up`. Если healthcheck включен, статус должен быть `Up ... (healthy)`.

## SLI/SLO кратко

SLI/SLO описаны на трех уровнях:

1. Технический уровень.
2. Модельный уровень.
3. Бизнес-уровень.

Краткая версия:

| Уровень | SLI | SLO |
|---|---|---|
| Технический | `/health` availability | HTTP 200 |
| Технический | Latency p95 | < 500 ms |
| Технический | 5xx error rate | < 1% |
| Технический | CPU usage | < 70% average |
| Технический | Memory usage | < 75% average |
| Модельный | MAE | < 100 |
| Модельный | RMSE | < 150 |
| Модельный | R2 | > 0.75 |
| Модельный | Data drift | PSI < 0.2 |
| Бизнес | Average cost estimation error | < 100 monetary units |
| Бизнес | Share of high-error predictions | < 5% |
| Бизнес | Correct margin band estimation | > 90% |

Так как задача является регрессионной, вместо классификационных метрик `AUC`, `Precision` и `Recall` используются `MAE`, `RMSE` и `R2`. Drift остается обязательной модельной метрикой, потому что распределение входных данных может меняться со временем.

Полная версия SLI/SLO находится в:

```text
monitoring/sli_slo.md
```

## Metrics Driven Development и ADR

```text
docs/adr/001-latency-mdd.md
```

В проекте выполнены следующие пункты:

| Требование | Где закрыто |
|---|---|
| Есть два набора данных метрик системы | ADR: existing system latency и improved system latency |
| Есть визуализация и сравнение распределений | ADR: раздел Analysis and visualization |
| Сформулированы H0 и H1 | ADR: раздел Hypotheses |
| Выбран уровень значимости p-value | ADR: `alpha = 0.05` |
| Проведен статистический тест | ADR: Mann-Whitney U test |
| Сделан вывод о принятии/отклонении H0 | ADR: раздел Test result |
| Решение оформлено в ADR | `docs/adr/001-latency-mdd.md` |
| В Decision зафиксировано архитектурное решение | ADR: раздел Decision |

Итоговое архитектурное решение: использовать Dockerized FastAPI service на облачной VM, потому что такой вариант дает воспроизводимый deployment, доступный healthcheck, возможность измерять latency и поддерживает дальнейшее развитие MLOps-пайплайна.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/train.py
pytest -q
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

## Docker run

```bash
sudo docker build -t standard-cost-service .
sudo docker run -d \\
  --name standard-cost-api \\
  --restart always \\
  -p 8000:8000 \\
  standard-cost-service
```

Если используется Docker Compose:

```bash
sudo docker compose up -d --build
```

или:

```bash
sudo docker-compose up -d --build
```

## Деинсталляция инфраструктуры

Через Docker Compose:

```bash
bash scripts/destroy.sh
```

Если контейнер запускался напрямую через Docker:

```bash
sudo docker stop standard-cost-api
sudo docker rm standard-cost-api
```

Дата окончания поддержания виртуальной машины: 31 июня 2026 года.
