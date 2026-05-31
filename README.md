# Standard Cost Prediction ML System

В этом репозитории хранится небольшой MLOps проект предсказания `standard_cost` на основе транзакционных данных для магазина.

## Бизнес-цель

Целью является предсказать стандартную цену на товар и поддерживать аналитику.

## ML

Тип: регрессия

Target:

```text
standard_cost
```

Основные метрики ML:

- MAE
- RMSE
- R2

Основная бизнес-метрика:

- средняя абсолютная стандартная ошибка оценки стоимости

## MLOps maturity level

Объявленный maturity level: 2.

Реализованные компоненты:

- версионирование кода через GitHub
- CI через GitHub Actions
- обслуживание моделей через FastAPI
- развертывание в Docker-контейнерах
- инфраструктура Docker Compose
- логирование экспериментов с моделями через MLflow
- описание конвейера переобучения
- конечная точка проверки работоспособности
- конечная точка метрик
- документация SLI/SLO
- ADR для разработки, основанной на метриках

## Локальная разработка

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

## Пример предсказания

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

## Облачная реализация

На облачной VM:

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/sohie21/ml-standard-cost-service.git
cd ml-standard-cost-service

bash scripts/bootstrap_vm.sh
newgrp docker

bash scripts/deploy_vm.sh
```

И далее открыть:

```text
http://YOUR_VM_PUBLIC_IP:8000/health
http://YOUR_VM_PUBLIC_IP:8000/docs
```

## Инфраструктура удаления модуля

```bash
bash scripts/destroy.sh
```

Дата окончания поддержания виртуальной машины: 31 июня 2026 года.
